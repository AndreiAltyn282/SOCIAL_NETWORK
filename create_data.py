from users.models import User
from posts.models import Post, Comment

# Функция для безопасного создания пользователя
def create_user_if_not_exists(username, password, email, **kwargs):
    try:
        user = User.objects.get(username=username)
        print(f"Пользователь {username} уже существует (ID: {user.id})")
        return user
    except User.DoesNotExist:
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            **kwargs
        )
        print(f"Создан новый пользователь: {username}")
        return user

# Создаём пользователей
alex = create_user_if_not_exists('alex', 'test123', 'alex@test.com', 
                                 position='Разработчик', is_expert=True)
maria = create_user_if_not_exists('maria', 'test123', 'maria@test.com', 
                                  position='Дизайнер')
ivan = create_user_if_not_exists('ivan', 'test123', 'ivan@test.com', 
                                 position='Менеджер')

# Создаём посты
print("\nСоздаём посты...")
post1 = Post.objects.create(
    author=alex, 
    text='Привет! Это мой первый пост в новой соцсети! Добро пожаловать!'
)
print(f"Пост 1 создан: {post1.text[:30]}...")

post2 = Post.objects.create(
    author=maria, 
    text='Дизайн - это не просто красиво, это удобно для пользователей!'
)
print(f"Пост 2 создан: {post2.text[:30]}...")

post3 = Post.objects.create(
    author=ivan, 
    text='Нужен фидбек по новому проекту! Жду ваши комментарии.'
)
print(f"Пост 3 создан: {post3.text[:30]}...")

post4 = Post.objects.create(
    author=alex, 
    text='Ищу разработчиков в команду. Отличные условия и дружный коллектив!'
)
print(f"Пост 4 создан: {post4.text[:30]}...")

# Создаём комментарии
print("\nСоздаём комментарии...")
Comment.objects.create(
    post=post1,
    author=maria,
    text='Отличный пост! Поддерживаю идею!'
)
print("Комментарий 1 создан")

Comment.objects.create(
    post=post1,
    author=alex,
    text='Спасибо! Ждём твой пост о дизайне!'
)
print("Комментарий 2 создан")

Comment.objects.create(
    post=post2,
    author=ivan,
    text='Отличный дизайн! Мне нравится!'
)
print("Комментарий 3 создан")

# Проверяем результат
print("\n" + "="*50)
print("ИТОГИ:")
print(f"Всего пользователей: {User.objects.count()}")
print(f"Всего постов: {Post.objects.count()}")
print(f"Всего комментариев: {Comment.objects.count()}")
print("="*50)

# Показываем всех пользователей
print("\nСписок пользователей:")
for user in User.objects.all():
    print(f"  - {user.username} (Эксперт: {user.is_expert})")

# Показываем посты с комментариями
print("\nПосты и комментарии:")
for post in Post.objects.all():
    print(f"\n  Пост от {post.author.username}:")
    print(f"    Текст: {post.text[:50]}...")
    comments = post.comments.all()
    if comments:
        print("    Комментарии:")
        for comment in comments:
            print(f"      - {comment.author.username}: {comment.text}")
    else:
        print("    Комментариев пока нет")

print("\nГотово! Теперь проверь API: http://127.0.0.1:8000/api/posts/")
exit()
