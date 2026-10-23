<?php
/**
 * Treści testowe do laboratorium CMS 2: opinie, FAQ, dane globalne
 * i strona główna złożona wyłącznie z bloków ACF.
 * Uruchomienie: wp eval-file seed_lab2.php <ID_obrazka_hero>
 * Wszystkie osoby i dane są fikcyjne.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

$hero_image = (int) ( $args[0] ?? 0 );

// --- Opinie (CPT opinia + pola ACF) -------------------------------------------
$opinie = array(
	array( 'Anna Z.', 'Kraków', 5, 'KNK-ETI-250', 'Etiopia pachnie jak kwiaty jaśminu. Paczka doszła następnego dnia, a w środku był odręczny liścik. Wracam po więcej!' ),
	array( 'Piotr W.', 'Gdańsk', 5, 'KNK-ESP-1000', 'Espresso Blend robi świetną cremę w moim ekspresie kolbowym. Czekoladowy, bez kwasowości – dokładnie tak jak lubię.' ),
	array( 'Kasia N.', 'Poznań', 4, 'KNK-V60', 'Drip V60 bardzo dobrej jakości. Minus za to, że instrukcja parzenia była tylko w internecie, ale obsługa szybko podesłała link.' ),
	array( 'Tomasz L.', 'Wrocław', 5, 'KNK-MLY', 'Młynek ręczny mieli równo i cicho. Po miesiącu codziennego używania – zero luzów. Polecam do dripa.' ),
	array( 'Ola M.', 'Łódź', 3, 'KNK-DEG-4', 'Zestaw degustacyjny fajny na prezent, ale jedna z kaw była dla mnie za kwaśna. Dobrze, że można spróbować kilku naraz.' ),
	array( 'Marek D.', 'Lublin', 5, 'KNK-KOL-1000', 'Kolumbia 1 kg starcza mi na miesiąc. Świeża data palenia, uczciwa cena. Biorę regularnie do biura.' ),
);
foreach ( $opinie as $i => list( $autor, $miasto, $ocena, $sku, $tresc ) ) {
	$id = wp_insert_post(
		array(
			'post_type'    => 'opinia',
			'post_status'  => 'publish',
			'post_title'   => $autor,
			'post_content' => $tresc,
			'post_date'    => gmdate( 'Y-m-d H:i:s', strtotime( '2026-10-01 10:00 +' . $i . ' days' ) ),
		)
	);
	update_field( 'ocena', (string) $ocena, $id );
	update_field( 'miasto', $miasto, $id );
	update_field( 'produkt', wc_get_product_id_by_sku( $sku ) ?: null, $id );
}

// --- FAQ (CPT faq) ----------------------------------------------------------------
$faq = array(
	array( 'Jak szybko wysyłacie zamówienia?', 'Zamówienia złożone do 13:00 w dni robocze wysyłamy tego samego dnia. Paczka zwykle dociera następnego dnia roboczego.' ),
	array( 'Od jakiej kwoty dostawa jest darmowa?', 'Dostawa kurierem i do paczkomatu jest darmowa od 199 zł. Poniżej tej kwoty kosztuje 12,99 zł (paczkomat) lub 14,99 zł (kurier).' ),
	array( 'Kawa ziarnista czy mielona?', 'Najwięcej aromatu daje kawa mielona tuż przed parzeniem. Jeśli nie masz młynka, wybierz kawę mieloną – mielimy ją pod ekspres przelewowy i drip.' ),
	array( 'Ile mam czasu na zwrot?', 'Masz 14 dni od otrzymania paczki na odstąpienie od umowy bez podania przyczyny. Produkt spożywczy musi być nieotwarty.' ),
	array( 'Jak przechowywać kawę?', 'W szczelnym pojemniku, w ciemnym i suchym miejscu, w temperaturze pokojowej. Nie trzymaj kawy w lodówce – chłonie zapachy i wilgoć.' ),
);
foreach ( $faq as $i => list( $pytanie, $odpowiedz ) ) {
	wp_insert_post(
		array(
			'post_type'    => 'faq',
			'post_status'  => 'publish',
			'post_title'   => $pytanie,
			'post_content' => $odpowiedz,
			'menu_order'   => $i,
		)
	);
}

// --- Dane globalne (Customizer) ---------------------------------------------------
set_theme_mod( 'kawanaklik_promo', 'Darmowa dostawa od 199 zł · kod JESIEN10 = −10% na kawy z Etiopii' );
set_theme_mod( 'kawanaklik_telefon', '+48 500 000 100' );
set_theme_mod( 'kawanaklik_email', 'kontakt@kawanaklik.test' );
set_theme_mod( 'kawanaklik_adres', "KawaNaKlik Sp. z o.o.\nul. Testowa 1, 31-000 Kraków" );
set_theme_mod( 'kawanaklik_facebook', 'https://example.com/kawanaklik-facebook' );
set_theme_mod( 'kawanaklik_instagram', 'https://example.com/kawanaklik-instagram' );

// --- Strona główna: wyłącznie bloki ACF ---------------------------------------------
/**
 * Buduje blok ACF w formacie zapisu edytora: wartości pól + odnośniki do kluczy pól.
 *
 * @param string $name   Nazwa bloku, np. acf/hero.
 * @param array  $fields nazwa_pola => [klucz_pola, wartość].
 */
function kawanaklik_seed_block( string $name, array $fields ): array {
	$data = array();
	foreach ( $fields as $field => list( $key, $value ) ) {
		$data[ $field ]       = $value;
		$data[ '_' . $field ] = $key;
	}
	return array(
		'blockName'    => $name,
		'attrs'        => array(
			'name' => $name,
			'data' => $data,
			'mode' => 'preview',
		),
		'innerBlocks'  => array(),
		'innerHTML'    => '',
		'innerContent' => array(),
	);
}

$usp = array( 'title' => array( 'field_knk_usp_title', 'Dlaczego KawaNaKlik?' ) );
$usp_items = array(
	array( '🔥', 'Świeżo palona', 'Palimy co tydzień – data palenia na każdej paczce.' ),
	array( '🚚', 'Wysyłka w 24 h', 'Zamówienia do 13:00 wysyłamy tego samego dnia.' ),
	array( '⭐', 'Kawy speciality', 'Tylko kawy z oceną SCA powyżej 80 punktów.' ),
	array( '💬', 'Pomoc baristy', 'Doradzimy kawę i sposób parzenia – napisz do nas.' ),
);
foreach ( $usp_items as $i => list( $icon, $title, $text ) ) {
	$n = $i + 1;
	$usp[ "usp_{$n}" ]       = array( "field_knk_usp_{$n}", '' );
	$usp[ "usp_{$n}_icon" ]  = array( "field_knk_usp_{$n}_icon", $icon );
	$usp[ "usp_{$n}_title" ] = array( "field_knk_usp_{$n}_title", $title );
	$usp[ "usp_{$n}_text" ]  = array( "field_knk_usp_{$n}_text", $text );
}

$blocks = array(
	kawanaklik_seed_block(
		'acf/hero',
		array(
			'title'  => array( 'field_knk_hero_title', 'Świeżo palona kawa speciality' ),
			'text'   => array( 'field_knk_hero_text', 'Kawa ziarnista i mielona z najlepszych farm, akcesoria do parzenia i zestawy prezentowe. Wysyłka w 24 h.' ),
			'image'  => array( 'field_knk_hero_image', $hero_image ),
			'button' => array(
				'field_knk_hero_button',
				array(
					'title'  => 'Przejdź do sklepu',
					'url'    => home_url( '/sklep/' ),
					'target' => '',
				),
			),
		)
	),
	kawanaklik_seed_block( 'acf/usp', $usp ),
	kawanaklik_seed_block(
		'acf/opinie',
		array(
			'title'      => array( 'field_knk_opinie_title', 'Opinie klientów' ),
			'count'      => array( 'field_knk_opinie_count', 3 ),
			'min_rating' => array( 'field_knk_opinie_min_rating', '4' ),
		)
	),
	kawanaklik_seed_block(
		'acf/faq',
		array(
			'title' => array( 'field_knk_faq_title', 'Najczęstsze pytania' ),
			'count' => array( 'field_knk_faq_count', 5 ),
		)
	),
	kawanaklik_seed_block(
		'acf/blog',
		array(
			'title' => array( 'field_knk_blog_title', 'Z bloga' ),
			'count' => array( 'field_knk_blog_count', 3 ),
		)
	),
);

$front_id = (int) get_option( 'page_on_front' );
wp_update_post(
	array(
		'ID'           => $front_id,
		'post_content' => serialize_blocks( $blocks ),
	)
);

WP_CLI::success( sprintf( 'Opinie: %d, FAQ: %d, strona główna (ID %d): %d bloków.', count( $opinie ), count( $faq ), $front_id, count( $blocks ) ) );
