# comfyui_psd

このコードは、ComfyUI に PSD ファイルを出力する機能を追加します。

使い方は、

1. まず PSDLayer ノードを作成し、image に画像を接続します。
2. レイヤー名前や合成モードを指定します。
3. 新しい PSDLayer ノードを作成します。
4. 先に作成した PSDLayer ノードの出力の PSD を、新しい PSDLayer の入力に入れて、同じように画像や名前やモードを指定します。
5. レイヤーを追加した順に、下から積み重なります。つまり最初の PSDLayer が一番背景になります。
6. 最後に Save PSD ノードに PSD を接続すると、最終的な PSD ファイルが保存されます。

This code adds functionality to export PSD files in ComfyUI.

How to use:

1. First, create a PSDLayer node and connect an image to it.
2. Specify the layer name and blend mode.
3. Create a new PSDLayer node.
4. Connect the PSD output from the previously created PSDLayer node to the input of the new PSDLayer, and specify the image, name, and mode in the same way.
5. Layers are stacked from bottom to top in the order they are added. This means the first PSDLayer becomes the background.
6. Finally, connect the PSD to the Save PSD node to save the final PSD file.

Note: This is an alpha/beta version, and some parts may not function properly yet.

# sample node

![image](https://github.com/user-attachments/assets/8c99ee84-6ac2-4451-8e7e-73a0f23ab9a3)

# sample result

![image](https://github.com/user-attachments/assets/3a0aa7bf-4c9c-4923-89f9-3bf6c7363cea)
