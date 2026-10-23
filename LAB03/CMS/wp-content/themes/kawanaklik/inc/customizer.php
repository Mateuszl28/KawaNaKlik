<?php
/**
 * Dane globalne sklepu w Customizerze (ACF Free nie ma strony opcji).
 * Odczyt w szablonach: kawanaklik_option( 'telefon' ).
 *
 * @package KawaNaKlik
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Lista ustawień: klucz => [etykieta, typ kontrolki, funkcja sanitize].
 */
function kawanaklik_option_fields(): array {
	return array(
		'promo'     => array( __( 'Pasek promocji (nad nagłówkiem)', 'kawanaklik' ), 'text', 'sanitize_text_field' ),
		'telefon'   => array( __( 'Telefon', 'kawanaklik' ), 'text', 'sanitize_text_field' ),
		'email'     => array( __( 'E-mail', 'kawanaklik' ), 'email', 'sanitize_email' ),
		'adres'     => array( __( 'Adres', 'kawanaklik' ), 'textarea', 'sanitize_textarea_field' ),
		'facebook'  => array( __( 'Facebook (URL)', 'kawanaklik' ), 'url', 'esc_url_raw' ),
		'instagram' => array( __( 'Instagram (URL)', 'kawanaklik' ), 'url', 'esc_url_raw' ),
	);
}

/**
 * Akcja customize_register – sekcja „Dane sklepu”.
 *
 * @param WP_Customize_Manager $wp_customize Menedżer Customizera.
 */
function kawanaklik_customize_register( WP_Customize_Manager $wp_customize ): void {
	$wp_customize->add_section(
		'kawanaklik_dane',
		array(
			'title'    => __( 'Dane sklepu', 'kawanaklik' ),
			'priority' => 30,
		)
	);

	foreach ( kawanaklik_option_fields() as $key => list( $label, $type, $sanitize ) ) {
		$wp_customize->add_setting(
			"kawanaklik_{$key}",
			array(
				'default'           => '',
				'sanitize_callback' => $sanitize,
				'transport'         => 'refresh',
			)
		);
		$wp_customize->add_control(
			"kawanaklik_{$key}",
			array(
				'label'   => $label,
				'section' => 'kawanaklik_dane',
				'type'    => $type,
			)
		);
	}
}
add_action( 'customize_register', 'kawanaklik_customize_register' );

/**
 * Zwraca daną globalną (surową – escapujemy przy wyświetlaniu).
 *
 * @param string $key Klucz bez prefiksu, np. 'telefon'.
 */
function kawanaklik_option( string $key ): string {
	return (string) get_theme_mod( "kawanaklik_{$key}", '' );
}
