import requests
import json
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
disable_warnings(InsecureRequestWarning)
import datetime
import os, sys

from log import my_logger
logger = my_logger(__name__)

class FortiApi():
    def __init__(self):
        """"""
        self.fg_addr = ''
        self.fg_user = ''
        self.fg_pass = ''
        self.fg_name = ''
        self.fg_hostname = ''

        self.base_url = f'https://{self.fg_addr}/api/v2/'
        self.session = requests.Session()
        self.session.verify = False

    def set_target(self, target):
        try:
            t = target.split(',')
            if not ( 3 <= len(t) <= 4 ):
                logger.error(f'ターゲット指定エラー: {target}')
                return False
            self.fg_addr = t[0]
            self.fg_user = t[1]
            self.fg_pass = t[2]
            self.fg_name = t[3] if 3 < len(t) else False
            self.base_url = f'https://{self.fg_addr}/api/v2/'
        except Exception as e:
            logger.error(str(e))
            return False
        return True

    def login(self):
        """"""
        login_data = {'username': self.fg_user, 'secretkey': self.fg_pass}
        login_check = False
        try:
            res = self.session.post(f'https://{self.fg_addr}/logincheck', data=login_data,)
            if res.status_code == 200:
                body_lines = res.content.decode('utf-8').split('\n')
                if len(body_lines) < 5:
                    logger.info(f'ログイン成功: {self.fg_addr}')
                    login_check = True
                else:
                    logger.info(f'ログイン失敗: {self.fg_addr}')
                    self.logout()
                    login_check = False
                    return False
            else:
                logger.info(f'ログイン失敗: {self.fg_addr}')
                self.logout()
                login_check = False
                print(res.content)
                return False
        except Exception as e:
            logger.error(e)
            login_check = False

        self.hostname = self.get_hostname()
        logger.info(f'ホスト名取得: {self.hostname} {self.fg_addr}')

        if not self.fg_name or self.fg_name is None:
            self.fg_name = self.hostname

        return login_check

    def logout(self):
        """"""
        res = self.session.post(f'https://{self.fg_addr}/logout')
        if res.status_code == 200:
            logger.info("ログアウト成功")
        else:
            logger.info("ログアウトが失敗しました")
        self.session.close()

    def backup(self, scope='global', backup_directory='./backup'):
        """"""
        backup_uri = f'{self.base_url}/monitor/system/config/backup?scope={scope}'
        backup_dir = os.path.abspath(backup_directory)

        logger.info(f'バックアップ開始: {self.hostname} {self.fg_addr}')

        res = self.session.get(backup_uri)

        if res.status_code == 200:
            logger.info(f'バックアップ取得: {self.hostname} {self.fg_addr}')
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f'{self.fg_name}_{timestamp}.conf'
            backup_file_path = os.path.join(backup_dir, filename)
            try:
                os.makedirs(backup_dir, exist_ok=True)
                with open(backup_file_path, 'wb') as file:
                    file.write(res.content)
            except Exception as e:
                logger.error(f'保存に失敗しました: {e}')
                self.logout()
                sys.exit()
            else:
                logger.info(f'{self.fg_name}のコンフィグを {backup_file_path} に保存しました')
        else:
            logger.error(f'バックアップ失敗: {self.fg_name} {self.fg_addr}, status code: {res.status_code}, response: {res.content}')

    def tac_report(self, scope='global', backup_directory='./backup'):
        """"""
        backup_uri = f'{self.base_url}/monitor/system/debug/download?scope={scope}'
        backup_dir = os.path.abspath(backup_directory)

        logger.info(f'Tac Report開始: {self.hostname} {self.fg_addr}')

        res = self.session.get(backup_uri)

        if res.status_code == 200:
            logger.info(f'Tac Report取得: {self.hostname} {self.fg_addr}')
            timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f'{self.fg_name}_{timestamp}_tacreport.log'
            tacreport_file_path = os.path.join(backup_dir, filename)
            try:
                os.makedirs(backup_dir, exist_ok=True)
                with open(tacreport_file_path, 'wb') as file:
                    file.write(res.content)
            except Exception as e:
                logger.error(f'保存に失敗しました: {e}')
                self.logout()
                sys.exit()
            else:
                logger.info(f'{self.fg_name}のTacReportを {tacreport_file_path} に保存しました')
        else:
            logger.error(f'Tac Report失敗: {self.fg_name} {self.fg_addr}, status code: {res.status_code}, response: {res.content}')

    def monitor_req(self, api_key, scoop='global', vdom='root', method='get'):
        """"""
        uri = f'{self.base_url}/monitor/{api_key}'

    def cmdb_req(self, api_key, method='get'):
        """"""
        uri = f'{self.base_url}/monitor'

    def run_backup(self, targets):
        self.set_target(targets)
    
    def get_hostname(self):
        uri = f'{self.base_url}/cmdb/system/global'
        res = self.session.get(uri)
        if res.status_code == 200:
            res_data = json.loads(res.content.decode('utf-8'))
        else:
            logger.error(f'code: {res.status_code}, body: {res.content}')
            self.logout()
            sys.exit()

        return res_data['results']['hostname']


if __name__ == '__main__':
    from argparse import ArgumentParser, RawTextHelpFormatter
    class MyArgumentParser(ArgumentParser):
        def error(self, message):
            print('error occured while parsing args : '+ str(message))
            self.print_help() 
            exit()
    from textwrap import dedent
    msg = dedent("""\
    ~~~ FortiGate Config Backup ~~~
    ## set target
    forti_backup -l 172.16.201.201,admin,P@ssw0rd

    ## target file csv
    forti_backup -f target.csv
    ### target csv format is "<fortigate addr>,<username>,<passwod>
    e.g.)
    ```
    172.16.201.201,admin,P@ssword
    172.16.201.202,nwadmin,mypassword
    ```
    """)

    parser = MyArgumentParser(description=msg, formatter_class=RawTextHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-l', '--list', help='ipaddr or hostname,user name,passward,(optional)nodename\ne.g.) forti_backup -l 172.16.201.201,admin,P@ssw0rd')
    group.add_argument('-f', '--file', help='target csv file\ne.g.) forti_backup -f target.csv\ncsv fromat sample)\n172.16.201.201,admin.P@ssword\n172.16.201.202,nwadmin,MyP@ssW0rd')
    parser.add_argument('-t', '--tac', action='store_true', help='get tac report')
    parser.add_argument('-d', '--dir', default='./fg_config', help='backup directory path default is ./fg_config')
    args = parser.parse_args()

    try:
        if args.list:
            fa = FortiApi()
            fa.set_target(args.list)
            fa.login()
            fa.backup(backup_directory=args.dir)
            if args.tac:
                fa.tac_report(backup_directory=args.dir)
            fa.logout()

        elif args.file:
            if not os.path.isfile(args.file):
                print(f'can not file open {os.path.abspath(args.file)}')
                sys.exit()

            with open(args.file, 'r', encoding='utf-8_sig') as f:
                targets = f.read().splitlines()

            print(os.path.abspath(args.file))

            for t in targets:
                fa = FortiApi()
                if not fa.set_target(t): continue
                if not fa.login(): continue
                fa.backup(backup_directory=args.dir)
                if args.tac:
                    fa.tac_report(backup_directory=args.dir)
                fa.logout()

    except KeyboardInterrupt:
        print('Ctrl + C')
    except Exception as e:
        print(e)
    finally:
        sys.exit()


