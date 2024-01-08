from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from .models import BookRecord, Friend, Group, Good, Chat
from .forms import BookRecordForm, GroupCheckForm, GroupSelectForm, FriendsForm, CreateGroupForm, PostForm, ChatForm

# indexのビュー関数
@login_required(login_url='/admin/login/')
def index(request, page=1):
    # publicのuserを取得
    (public_user, public_group) = get_public()
    
    # POST送信時の処理
    if request.method == 'POST':
        
        # Groupsのチェックを更新したときの処理
        # フォームの用意
        checkform = GroupCheckForm(request.user, request.POST)
        # チェックされたGroup名をリストにまとめる
        glist = []
        for item in request.POST.getlist('groups'):
            glist.append(item)
        # BookRecordの取得
        bookrecord = get_your_group_bookrecord(request.user, glist, page)
        
    # GETアクセス時の処理
    else:
        # フォームの用意
        checkform = GroupCheckForm(request.user)
        # Groupのリストを取得
        gps = Group.objects.filter(owner=request.user)
        glist = [public_group.title]
        for item in gps:
            glist.append(item.title)
        # BookRecordの取得
        bookrecord = get_your_group_bookrecord(request.user, glist, page)
    
    # 共通処理
    params = {
        'login_user': request.user,
        'contents': bookrecord,
        'check_form': checkform,
    }
    return render(request, 'books/index.html', params)

@login_required(login_url='/admin/login/')
def groups(request):
    # 自分が登録したFriendを取得
    friends = Friend.objects.filter(owner=request.user)
    
    # POST送信時の処理
    if request.method == 'POST':
        
        # Groupsメニュー選択肢の処理
        if request.POST['mode'] == '__groups_form__':
            # 選択したGroup名を取得
            sel_group = request.POST['groups']
            # Groupを取得
            gp = Group.objects.filter(owner=request.user).filter(title=sel_group).first()
            # Groupに含まれるFriendを取得
            fds = Friend.objects.filter(owner=request.user).filter(group=gp)
            print(Friend.objects.filter(owner=request.user))
            # FriendのUserをリストにまとめる
            vlist = []
            for item in fds:
                vlist.append(item.user.username)
            # フォームの用意
            groupsform = GroupSelectForm(request.user, request.POST)
            friendsform = FriendsForm(request.user, friends=friends, vals=vlist)
        # Friendsのチェック更新時の処理
        if request.POST['mode'] == '__friends_form__':
            # 選択したGroupを取得
            try:
                sel_group = request.POST['group']
                group_obj = Group.objects.filter(title=sel_group).first()
                print(group_obj)
                # チェックしたFriendsを取得
                sel_fds = request.POST.getlist('friends')
                # FriendsのUserを取得
                sel_users = User.objects.filter(username__in=sel_fds)
                # Userのリストに含まれるユーザーが登録したFriendを取得
                fds = Friend.objects.filter(owner=request.user).filter(user__in=sel_users)
                # すべてのFriendにGroupを設定し保存
                vlist = []
                for item in fds:
                    item.group = group_obj
                    item.save()
                    vlist.append(item.user.username)
                # メッセージを設定
                messages.success(request, 'チェックされたFriendを' + sel_group + 'に登録しました。')
                # フォームの用意
                groupsform = GroupSelectForm(request.user, {'groups': sel_group})
                friendsform = FriendsForm(request.user, friends=friends, vals=vlist)
            except:
                messages.success(request, "グループを選択してください。")
                groupsform = GroupSelectForm(request.user)
                friendsform = FriendsForm(request.user, friends=friends, vals=[])
            
    # GETアクセス時の処理
    else:
        # フォームの用意
        groupsform = GroupSelectForm(request.user)
        friendsform = FriendsForm(request.user, friends=friends, vals=[])
        sel_group = '-'
    # 共通処理
    createform = CreateGroupForm()
    params = {
        'login_user': request.user,
        'groups_form': groupsform,
        'friends_form': friendsform,
        'create_form': createform,
        'group': sel_group,
    }
    return render(request, 'books/groups.html', params)
    
# Friendの追加処理
@login_required(login_url='/admin/login/')
def add(request):
    # 追加するUserを取得
    add_name = request.GET['name']
    add_user = User.objects.filter(username=add_name).first()
    # Userが本人だった場合の処理
    if add_user == request.user:
        messages.info(request, "自分自身をFriendに追加することはできません。")
        return redirect(to='/books')
    # publicの取得
    (public_user, public_group) = get_public()
    # add_userのFriendの数を調べる
    frd_num = Friend.objects.filter(owner=request.user).filter(user=add_user).count()
    # ゼロより大きければすでに登録済み
    if frd_num > 0:
        messages.info(request, add_user.username + 'は既に追加されています。')
        return redirect(to='/books')
    # ここからFriendの登録処理
    else:
        frd = Friend()
        frd.owner = request.user
        frd.user = add_user
        frd.group = public_group
        frd.save()
        # メッセージを設定
        messages.success(request, add_user.username + 'を追加しました！\
            groupページに移動して、追加したFriendをメンバーに設定してください。')
        return redirect(to='/books/groups')

# グループの作成処理
@login_required(login_url='/admin/login/')
def creategroup(request):
    # Groupを作り、Userとtitleを設定して保存
    gp = Group()
    gp.owner = request.user
    gp.title = request.user.username + 'の' + request.POST['group_name']
    gp.save()
    messages.info(request, '新しいグループを作成しました。')
    return redirect(to='/books/groups')
    
    
# 読書記録のポスト処理
@login_required(login_url='/admin/login/')
def post(request):
    # POST送信の処理
    if request.method == 'POST':
        # 送信内容の処理
        gr_name = request.POST['group']
        title = request.POST['title']
        first_author = request.POST['first_author']
        pub_year = request.POST['pub_year']
        genre = request.POST['genre']
        score = request.POST['score']
        summary = request.POST['summary']
        report = request.POST['report']
        # Groupの取得
        group = Group.objects.filter(owner=request.user).filter(title=gr_name).first()
        if group == None:
            (pub_user, group) = get_public()
        # BookRecordを作成して保存
        brcd = BookRecord()
        brcd.owner = request.user
        brcd.group = group
        brcd.title = title
        brcd.first_author = first_author
        brcd.pub_year = pub_year
        brcd.genre = genre
        brcd.score = score
        brcd.summary = summary
        brcd.report = report
        brcd.save()
        # メッセージを設定
        messages.success(request, '新しいRecordを投稿しました！')
        return redirect(to='/books')
    
    # GETアクセス時の処理
    else:
        form = PostForm(request.user)
        
    # 共通処理
    params = {
        'login_user': request.user,
        'form': form,
    }
    return render(request, 'books/post.html', params)

# goodボタンの処理
@login_required(login_url='/admin/login/')
def good(request, good_id):
    # goodするBookRecordを取得
    good_brcd = BookRecord.objects.get(id=good_id)
    # 自分がメッセージにGoodした数を調べる
    is_good = Good.objects.filter(owner=request.user).filter(bookrecord=good_brcd).count()
    # ゼロより大きければすでにgood済み
    if is_good > 0:
        messages.success(request, 'すでにメッセージにはGoodしています。')
        return redirect(to='/books')
    
    # BookRecordのgood_countを1増やす
    good_brcd.good_count += 1
    good_brcd.save()
    # Goodを作成し、設定して保存
    good = Good()
    good.owner = request.user
    good.bookrecord = good_brcd
    good.save()
    # メッセージを設定
    messages.success(request, 'RecordにGoodしました！')
    return redirect(to='/books')

# chatボタンの処理
@login_required(login_url='/admin/login/')
def chat_button(request, chat_id):
    # chatするBookRecordを取得
    chat_brcd = BookRecord.objects.get(id=chat_id)
    print(chat_brcd, "ボタン")
    messages.success(request, 'Chatページに移行します！')
    return redirect(to="/books/chat.html")

# chatのビュー関数
@login_required(login_url='/admin/login/')
def chat(request, chat_id):
    chat_theme = BookRecord.objects.get(id=chat_id)
    print(chat_theme, "ビュー")
    # POST送信時の処理
    if request.method == 'POST':
        # 送信内容の処理
        comment = request.POST['comment']
        # Chatを作成して保存
        chat = Chat()
        chat.owner = request.user
        chat.bookrecord = chat_theme
        chat.comment = comment
        form = ChatForm()
        chat.save()
        print("POST OK")
        chat = Chat.objects.filter(bookrecord=chat_theme)
    # GETアクセス時の処理
    else:
        form = ChatForm()
        print("GETのフォーム OK")
        chat = Chat.objects.filter(bookrecord=chat_theme)
        print(chat, "GETのchat OK")
    # 共通処理
    params = {
        'login_user': request.user,
        'brcd_contents': chat_theme,
        'chat_contents': chat,
        'form': form,
        'id': chat_id,
    }
    return render(request, 'books/chat.html', params)

# Editのビュー関数    
def edit(request, edit_id):
    brcd = BookRecord.objects.get(id=edit_id)
    print("BookRecord選択OK")
    if brcd.owner != request.user:
        messages.success(request, '自分のでないレコードは編集できません。')
        return redirect(to='/books')
    # POST送信時の処理
    if (request.method == 'POST'):
        reviced = BookRecordForm(request.POST, instance=brcd)
        reviced.save()
        return redirect(to='/books')
    # GETアクセス時の処理
    # 共通処理
    params = {
        'login_user': request.user,
        'id': edit_id,
        'form': BookRecordForm(instance=brcd),
    }
    return render(request, 'books/edit.html', params)

# Deleteのビュー関数
def delete(request, del_id):
    brcd = BookRecord.objects.get(id=del_id)
    # POST送信時の処理
    if (request.method == 'POST'):
        brcd.delete()
        messages.success(request, 'レコードを削除しました。')
        return redirect(to='books')
    # GETアクセス時の処理
    # 共通処理
    params = {
        'login_user': request.user,
        'id': del_id,
        'contents': brcd,
    }
    return render(request, 'books/delete.html', params)


    
# 以降は普通の関数=====================================================================

# 指定されたグループおよび検索文字によるBookRecordの取得
def get_your_group_bookrecord(owner, glist, page):
    page_num = 5 # ページ当たりの表示数
    # publicの取得
    (public_user, public_group) = get_public()
    # チェックされたGroupの取得
    groups = Group.objects.filter(Q(owner=owner) | Q(owner=public_user)).filter(title__in=glist)
    # Groupに含まれるFriendの取得
    me_friends = Friend.objects.filter(group__in=groups)
    # FriendのUserをリストにまとめる
    me_users = []
    for f in me_friends:
        me_users.append(f.user)
    # UserリストのUserが作ったGroupの取得
    his_groups = Group.objects.filter(owner__in=me_users)
    his_friends = Friend.objects.filter(user=owner).filter(group__in=his_groups)
    me_groups = []
    for hf in his_friends:
        me_groups.append(hf.group)
    # Groupがgroupsかme_groupsに含まれるBookRecordの取得
    bookrecords = BookRecord.objects.filter(Q(group__in=groups) | Q(group__in=me_groups))
    # ページネーションで指定ページを取得
    page_item = Paginator(bookrecords, page_num)
    return page_item.get_page(page)
    
# publicなUserとGroupを取得する
def get_public():
    public_user = User.objects.filter(username='public').first()
    public_group = Group.objects.filter(owner=public_user).first()
    return (public_user, public_group)


