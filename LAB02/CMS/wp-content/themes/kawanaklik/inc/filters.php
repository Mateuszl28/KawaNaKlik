<?php
/**
 * Filtry zmieniające domyślne wartości WordPressa.
 *
 * @package KawaNaKlik
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Filtr excerpt_length – zajawka ma 20 słów zamiast 55. Filtr MUSI zwrócić wartość.
 *
 * @param int $length Domyślna długość zajawki.
 */
function kawanaklik_excerpt_length( int $length ): int {
	return 20;
}
add_filter( 'excerpt_length', 'kawanaklik_excerpt_length' );

/**
 * Filtr excerpt_more – zamienia „[…]” na wielokropek.
 *
 * @param string $more Domyślny znacznik końca zajawki.
 */
function kawanaklik_excerpt_more( string $more ): string {
	return '…';
}
add_filter( 'excerpt_more', 'kawanaklik_excerpt_more' );
