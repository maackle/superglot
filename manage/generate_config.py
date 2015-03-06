from string import Template


def write_nginx_config():

    root = '/home/superglot/server'
    logroot = '/var/log/nginx/superglot'

    proxy_config = '''
        proxy_pass http://127.0.0.1:6107;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        proxy_read_timeout 600;
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        send_timeout 600;
    '''

    result = Template('''

server {
    listen 80;
    server_name superglot.com;
    access_log  $logroot/access.log;
    error_log  $logroot/error.log;

    location /favicon.ico {
        autoindex on;
        alias $root/superglot/static/favicon.ico;
    }

    location /static {
        autoindex on;
        alias $root/superglot/static/;
    }

    location /media {
        autoindex on;
        alias $root/superglot/media/;
    }

    location / {
        $proxy_config
        location /register {
            $proxy_config
            auth_basic "Alpha access only";
            auth_basic_user_file $root/conf/htpasswd;
        }

    }

    # error_page 404 /media/404.html;
    # error_page 500 502 503 504 /media/50x.html;
}
    ''').substitute(
        root=root,
        logroot=logroot,
        proxy_config=proxy_config
    )

    print(result)

    # with open('conf/nginx.conf', 'w') as f:
    #     f.write(result)

