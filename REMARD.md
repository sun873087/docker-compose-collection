
# Google Gmail SMTP Password 

1. 登入你的 Google 帳戶。
2. 前往 👉 [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. 選擇應用程式類型（例如：Mail），裝置名稱隨便填。
4. Google 會產生一組 16 位元的密碼，這個就是 `smtp_password`。

```ruby
gitlab_rails['smtp_password'] = "abcd efgh ijkl mnop"  # 不用空格也可以
```