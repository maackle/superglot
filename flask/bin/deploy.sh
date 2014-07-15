rsync -av \
--exclude __pycache__ \
--exclude node_modules \
--exclude .flask-cache \
--exclude .sass-cache \
--exclude .git \
--exclude .DS_Store \
./ michael@superglot.com:/var/www/superglot.com/
