# どみとる
## 概要
どみとるのバックエンドシステム

## 使用技術
Python 3.12.4  
Flask 3.03  
Mysql 8.3.0

# WebAPI
## セットアップ
0. DBのセットアップを済ませる。
1. `requirements.txt`に書かれたpythonパッケージをインストールする
2. `.env`ファイルを作成し、環境変数を設定する
3. `main.py`を実行する

## 環境変数
| 変数名 | 説明 |
| --- | --- |
| DB\_CONFIG\_JSON | Mysqlへアクセスする際のユーザ情報を記したJSONファイルへのパス。 |
| DB\_IOT\_INSERTER | IoTDataテーブルへデータを挿入するMysqlのユーザ情報を記したJSONファイルへのパス。デフォルトでは`DB\_CONFIG\_JSON`と同じとなる。 |
| FRONTEND\_URL | フロントエンドのURL |
| MODEL\_PATH | YOLOのモデルファイルへのパス |
| SECRET\_KEY | シークレットキー |

# DB
## セットアップ
1. `db/product.sql`内のsqlを実行する
2. `config.sql`を元にユーザを追加する

# データ解析
## セットアップ
0. DBのセットアップを済ませる。
1. `data_analysis/event_requirements.txt`のpythonパッケージをインストールする
2. `python data_analysis/event.py`を実行するか、`data_analysis/event.sh`を実行する
