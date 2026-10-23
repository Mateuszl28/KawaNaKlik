<?php
/**
 * Plugin Name: KawaNaKlik – webhooki do lokalnego n8n (tylko DEV)
 * Description: WooCommerce domyślnie blokuje webhooki na adresy lokalne (localhost). Na lokalnym środowisku
 *              laboratoryjnym dopuszczamy wyłącznie localhost:5690, gdzie działa n8n. NIE używać na produkcji.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

add_filter(
	'http_request_host_is_external',
	static function ( $external, $host, $url ) {
		return ( 'localhost' === $host && 5690 === (int) wp_parse_url( $url, PHP_URL_PORT ) ) ? true : $external;
	},
	10,
	3
);

// wp_http_validate_url() dopuszcza domyślnie tylko porty 80, 443 i 8080.
add_filter(
	'http_allowed_safe_ports',
	static function ( $ports ) {
		$ports[] = 5690;
		return $ports;
	}
);

// Webhooki wysyłamy od razu (synchronicznie), żeby testy nie czekały na WP-Cron.
add_filter( 'woocommerce_webhook_deliver_async', '__return_false' );
