<?php
$cfg = json_decode(file_get_contents('/boot/config/plugins/dns-watcher/config.json'), true);
function safe($k) {
  global $cfg;
  return isset($cfg[$k]) ? htmlspecialchars($cfg[$k]) : '';
}
?>
<form method='post' action='/plugins/dns-watcher/save.php'>
  <label>DNS API URL: <input name='DNS_API_URL' value='<?=safe("DNS_API_URL")?>' /></label><br>
  <label>API Key: <input type='password' name='API_KEY' value='<?=safe("API_KEY")?>' /></label><br>
  <label>Default Domain: <input name='DEFAULT_DOMAIN' value='<?=safe("DEFAULT_DOMAIN")?>' /></label><br>
  <label>Prefix: <input name='hostname_prefix' value='<?=safe("hostname_prefix")?>' /></label><br>
  <label>Suffix: <input name='hostname_suffix' value='<?=safe("hostname_suffix")?>' /></label><br>
  <button type='submit'>Save</button>
</form>
<form method='post' action='/plugins/dns-watcher/restart.php'>
  <button type='submit'>Restart Watcher</button>
</form>
