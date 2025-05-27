<?php
shell_exec("pkill -f dns-watcher.py && /usr/local/sbin/dns-watcher.py &");
echo "🔄 Watcher restarted.";
?>