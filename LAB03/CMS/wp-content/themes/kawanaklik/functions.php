<?php
/**
 * Funkcje motywu KawaNaKlik – tylko dołącza pliki z inc/.
 *
 * @package KawaNaKlik
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit; // Blokada bezpośredniego wywołania pliku.
}

require get_theme_file_path( 'inc/setup.php' );
require get_theme_file_path( 'inc/assets.php' );
require get_theme_file_path( 'inc/widgets.php' );
require get_theme_file_path( 'inc/filters.php' );
require get_theme_file_path( 'inc/template-tags.php' );
require get_theme_file_path( 'inc/post-types.php' );
require get_theme_file_path( 'inc/blocks.php' );
require get_theme_file_path( 'inc/customizer.php' );
