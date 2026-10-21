<?php
/**
 * Dołączanie arkuszy stylów i skryptów.
 *
 * @package KawaNaKlik
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Akcja wp_enqueue_scripts – kolejkuje CSS i JS motywu.
 * Wersja z nagłówka style.css wymusza odświeżenie plików w przeglądarce po zmianie.
 */
function kawanaklik_assets(): void {
	$ver = wp_get_theme()->get( 'Version' );

	wp_enqueue_style( 'kawanaklik-main', get_theme_file_uri( 'assets/css/main.css' ), array(), $ver );
	wp_enqueue_script( 'kawanaklik-main', get_theme_file_uri( 'assets/js/main.js' ), array(), $ver, array( 'strategy' => 'defer' ) );
}
add_action( 'wp_enqueue_scripts', 'kawanaklik_assets' );
