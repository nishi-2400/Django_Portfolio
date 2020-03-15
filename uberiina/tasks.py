# from django.core.mail import send_mail
# from django.conf import settings
# from django.template.loader import get_template



# # # メール送信
# # @shared_task
# # def send_email(message):
# #     subject = 'テストメールです'
# #     from_email = settings.DEFAULT_FROM_EMAIL
# #     recipient_list = ['a7w21087bump@yahoo.co.jp']
# #     send_mail(subject, message, from_email, recipient_list)

# # # メールの本文を作成
# # def get_message(greeting):
# #     template = get_template('mail/message.txt')
# #     params = {
# #         'greeting': greeting,
# #     }
# #     message = template.render(params)
# #     return message

# # def send_notification(greeting):
# #     message = get_message(greeting)
# #     send_email(message)