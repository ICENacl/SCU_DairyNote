# SCU DairyNote

作者邮箱：icexyz787@gmail.com

本程序的目的是实现每日自动打卡，避免每天定闹钟打卡:)

本程序主要使用Python的[Request](https://docs.python-requests.org/zh_CN/latest/)库来发送Http请求

目前主要方式是通过Cokkies来绕开登录。原本的想法是模拟登录，奈何主流的使用tesseract的方法识别验证码正确率过低，因此暂时使用cookies的方法来绕开登录