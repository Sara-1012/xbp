import random

#タイトル
print("1/100を引かなきゃ終わらないクソゲー")

#名前入力
name=input("あなたの名前を教えてください")
print("こんにちは！",name,"さん！運試しをしましょう！")

#ゲーム本体
count=0 #繰り返した回数を数えられる

while True: #無限ループ
    user=input("引きますか？( Enter=引く / q=やめる)") #入力
    if user.lower()=="q": #やめるver
        print(name,"さんは途中でやめました。残念です…")
        break

    result=random.randint(1,101) #1~100の乱数
    count+=1 #繰り返し回数に＋１する

    if result==1: #当たりver
        print("✨当たり！✨")
        print(name,"さんは",count,"回目で当たりました！やったね！")
        print("ゲーム終了！こんなクソゲーをやってくれてありがとう！")
        break #ここにbreak入れると当たった時ゲームが終わる
    else: #ハズレver
        print("❌ハズレ❌")
        print("現在",count,"回目です。早く当たるといいね！")
        #ここに絶対に！！！break入れない！！！ハズレの時繰り返されなくなるから！！！