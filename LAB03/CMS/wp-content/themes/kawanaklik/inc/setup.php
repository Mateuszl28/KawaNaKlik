<?php
/**
 * Konfiguracja motywu: wsparcie funkcji WordPressa i lokalizacje menu.
 *
 * @package KawaNaKlik
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Akcja after_setup_theme – uruchamiana raz, zaraz po wczytaniu functions.php.
 */
function kawanaklik_setup(): void {
	add_theme_support( 'title-tag' );        // WordPress sam generuje <title>.
	add_theme_support( 'post-thumbnails' );  // Obrazki wyróżniające.
	add_theme_support( 'html5', array( 'search-form', 'gallery', 'caption', 'style', 'script' ) );
	add_theme_support( 'custom-logo' );

	register_nav_menus(
		array(
			'primary' => __( 'Menu główne', 'kawanaklik' ),
			'footer'  => __( 'Menu w stopce', 'kawanaklik' ),
		)
	);
}
add_action( 'after_setup_theme', 'kawanaklik_setup' );
