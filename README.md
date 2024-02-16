## Forti Backup
### 使い方
「実行ディレクトリ/fg_config/」配下にコンフィグ、Tac Reportを保存

* ターゲット直接指定
```powershell
forti_config_backup -l 192.0.2.1,user,password
```

* tac reportも取得
```powershell
forti_config_backup -l 192.0.2.1,user,password
```

* ターゲット複数指定（CSV）
```powershell
forti_config_backup -f target.csv
```

target csv format is "<fortigate addr>,<username>,<passwod>
e.g.)
```
192.0.2.1,user,password
192.0.2.2,nwadmin,nwpassword
```

### セットアップ
例）
`c:\opt\appz`配下に展開, `c:\opt\bin`配下にsymlink作成

DOSコマンドプロンプトでsymlink作成（Powershellでのsymlnk作成がいまひとつ分からなかった・・・）
```dos
mklink C:\opt\bin\forti_config_backup.exe C:\opt\appz\forti_config_backup\forti_config_backup.exe
```

PATHが通ってなければ`c:\opt\bin`をPATHに追加
Powershellの場合
```powershell
$new_dir = "c:\opt\bin"
$new_path = [Environment]::GetEnvironmentVariable("Path", "User")
$new_path += ";$new_dir"
[Environment]::SetEnvironmentVariable("Path", $new_path, "User")
```

### セットアップ（scoop)

