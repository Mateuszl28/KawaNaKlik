<?php
/**
 * Własne typy treści: opinie klientów i FAQ.
 *
 * @package KawaNaKlik
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Akcja init – rejestracja typów treści.
 */
function kawanaklik_register_post_types(): void {
	register_post_type(
		'opinia',
		array(
			'labels'       => array(
				'name'          => __( 'Opinie', 'kawanaklik' ),
				'singular_name' => __( 'Opinia', 'kawanaklik' ),
				'add_new_item'  => __( 'Dodaj opinię', 'kawanaklik' ),
				'edit_item'     => __( 'Edytuj opinię', 'kawanaklik' ),
				'all_items'     => __( 'Wszystkie opinie', 'kawanaklik' ),
			),
			'public'       => true,
			'has_archive'  => true,                     // Archiwum pod /opinie/.
			'rewrite'      => array( 'slug' => 'opinie' ),
			'menu_icon'    => 'dashicons-format-quote',
			'supports'     => array( 'title', 'editor', 'thumbnail' ),
			'show_in_rest' => true,                     // Edytor blokowy + REST API.
		)
	);

	// FAQ jako CPT – w ACF Free nie ma pola Repeater.
	register_post_type(
		'faq',
		array(
			'labels'             => array(
				'name'          => __( 'FAQ', 'kawanaklik' ),
				'singular_name' => __( 'Pytanie FAQ', 'kawanaklik' ),
				'add_new_item'  => __( 'Dodaj pytanie', 'kawanaklik' ),
				'edit_item'     => __( 'Edytuj pytanie', 'kawanaklik' ),
				'all_items'     => __( 'Wszystkie pytania', 'kawanaklik' ),
			),
			'public'             => false,
			'show_ui'            => true,
			'show_in_rest'       => true,
			'publicly_queryable' => false,
			'menu_icon'          => 'dashicons-editor-help',
			'supports'           => array( 'title', 'editor', 'page-attributes' ),
		)
	);
}
add_action( 'init', 'kawanaklik_register_post_types' );
