PyPiano
=======

A piano game written in Python 2.7 with pygame, compatible with numbered musical notation, 88 keys.

Dependences:
> pygame<br>
> wx

此软件完全按照简谱设计，可选择多个音调，自带变调夹功能，指法统一。

当选择完音调后，点击演奏即可开始演奏。ASDFJKL对应当前音调的7个音，QWERUIO对应高八度7个音，ZXCVM,.对应低八度七个音，大小写无影响。T/Y降低/提高全部按键8度，space重置。G/H切换上一个/下一个音调。回车键结束演奏。

演奏完成后可保存录音（特殊格式），亦可回放录音。
