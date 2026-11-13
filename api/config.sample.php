<?php
/*
 * Copy this file to config.php (same folder) and fill in your key. config.php is NOT part of the zip or the
 * repository on purpose: the key lives only on your Hostinger server.
 */
return [
    // Your Anthropic API key (console.anthropic.com). Leave empty to keep Wallie on the built-in local answers.
    'api_key' => '',

    // Models. Haiku is the cheap, fast one for Wallie; use a larger model for the Pro chat if you want.
    'model_wallie' => 'claude-haiku-5-5',
    'model_chat'   => 'claude-sonnet-5-5',

    // Spending guards: questions per visitor per hour, and in total per day for the whole site.
    'limit_per_hour' => 20,
    'limit_per_day'  => 500,

    // Only needed if the site is reached under a different host than the one the browser shows (rare).
    'allowed_hosts' => [],

    // If Hostinger sits behind a proxy that hides visitors' IPs, name the header that carries the real one,
    // for example 'HTTP_CF_CONNECTING_IP'. Leave empty otherwise.
    'client_ip_header' => '',
];
