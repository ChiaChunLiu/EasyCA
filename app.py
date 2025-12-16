import os
import subprocess
import zipfile
import ipaddress
import glob
from flask import Flask, render_template, request, send_file, after_this_request

app = Flask(__name__)

# 設定路徑
CAROOT = os.getenv("CAROOT", "/root/.local/share/mkcert")
CERT_DIR = "/app/certs"

# 確保目錄存在
os.makedirs(CERT_DIR, exist_ok=True)
os.makedirs(CAROOT, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download-ca')
def download_ca():
    """下載根憑證 (Root CA) 讓使用者安裝"""
    ca_path = os.path.join(CAROOT, "rootCA.pem")
    if os.path.exists(ca_path):
        return send_file(ca_path, as_attachment=True, download_name="rootCA.pem")
    return "尚未初始化 Root CA，請檢查伺服器日誌。", 404

@app.route('/generate', methods=['POST'])
def generate():
    target_ip = request.form.get('ip')
    
    # 1. 驗證 IP 格式
    try:
        ipaddress.ip_address(target_ip)
    except ValueError:
        return "無效的 IP 位址格式", 400

    # 2. 準備生成
    os.chdir(CERT_DIR)
    
    # 清除該 IP 可能存在的舊暫存檔
    for f in glob.glob(f"*{target_ip}*"):
        try: os.remove(f)
        except: pass

    # 3. 呼叫 mkcert 生成憑證
    # 這裡同時簽發給 IP 和 IP.local (方便某些 mDNS 應用)
    try:
        subprocess.run(["mkcert", target_ip], check=True)
    except subprocess.CalledProcessError:
        return "憑證生成失敗", 500

    # 4. 尋找生成的檔案
    try:
        # mkcert 預設命名規則： <ip>.pem 或 <ip>+1.pem
        pem_file = glob.glob(f"*{target_ip}*.pem")[0] 
        key_file = glob.glob(f"*{target_ip}*-key.pem")[0]
    except IndexError:
        return "找不到生成的檔案", 500

    # 5. 打包成 ZIP
    zip_filename = f"{target_ip}-ssl.zip"
    zip_path = os.path.join(CERT_DIR, zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w') as zf:
        zf.write(pem_file, arcname="server.crt") # 統一改名為 server.crt
        zf.write(key_file, arcname="server.key") # 統一改名為 server.key

    # 6. 下載後自動刪除伺服器上的暫存檔
    @after_this_request
    def remove_files(response):
        try:
            os.remove(zip_path)
            os.remove(pem_file)
            os.remove(key_file)
        except Exception as e:
            app.logger.error(f"清理檔案失敗: {e}")
        return response

    return send_file(zip_path, as_attachment=True)

if __name__ == '__main__':
    # 1. 檢查 CA 初始化
    ca_cert = os.path.join(CAROOT, "rootCA.pem")
    if not os.path.exists(ca_cert):
        print("🚀 初次啟動：正在初始化 mkcert Root CA...")
        subprocess.run(["mkcert", "-install"], check=True)

    # 2. 設定 Port
    port = int(os.environ.get("PORT", 7777))

    # 3. 檢查是否有 SSL 憑證 (智慧切換)
    ssl_cert_path = "/app/ssl/server.crt"
    ssl_key_path = "/app/ssl/server.key"
    
    # 檢查檔案是否存在且有內容
    if os.path.exists(ssl_cert_path) and os.path.exists(ssl_key_path):
        print(f"🔒 偵測到憑證，啟動 HTTPS 模式 (Port {port})")
        # ssl_context 參數會啟用 SSL
        app.run(host='0.0.0.0', port=port, ssl_context=(ssl_cert_path, ssl_key_path))
    else:
        print(f"⚠️ 未偵測到憑證，啟動 HTTP 模式 (Port {port})")
        print("💡 提示：您可以生成本機 IP 的憑證，並放入 ./ssl 資料夾重啟即可啟用 HTTPS。")
        app.run(host='0.0.0.0', port=port)