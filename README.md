# comfyui_psd

このコードは、ComfyUI に PSD ファイルを出力する機能を追加します。

まだテスト版であり、正常に動作しない可能性や、環境を壊す可能性があります。

# install 

    cd ComfyUI\custom_nodes
    git clone https://github.com/sugarkwork/comfyui_psd.git
    cd comfyui_psd
    .\install.bat

install.bat を叩く必要があります。

上手く動かないかもしれません……。

# how to use

使い方は、

1. まず PSDLayer ノードを作成し、image に画像を接続します。
2. レイヤー名前や合成モードを指定します。
3. 新しい PSDLayer ノードを作成します。
4. 先に作成した PSDLayer ノードの出力の PSD を、新しい PSDLayer の入力に入れて、同じように画像や名前やモードを指定します。
5. レイヤーを追加した順に、下から積み重なります。つまり最初の PSDLayer が一番背景になります。
6. 最後に Save PSD ノードに PSD を接続すると、最終的な PSD ファイルが保存されます。


# sample node

![image](https://github.com/user-attachments/assets/8c99ee84-6ac2-4451-8e7e-73a0f23ab9a3)

# sample result

![image](https://github.com/user-attachments/assets/3a0aa7bf-4c9c-4923-89f9-3bf6c7363cea)
