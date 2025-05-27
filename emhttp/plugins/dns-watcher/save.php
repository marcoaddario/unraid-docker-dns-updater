<?php
$data = $_POST;
file_put_contents('/boot/config/plugins/dns-watcher/config.json', json_encode($data, JSON_PRETTY_PRINT));
echo "✅ Saved. Reloading...";
shell_exec("pkill -f dns-watcher.py && /usr/local/sbin/dns-watcher.py &");
?>