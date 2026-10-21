<?php
/**
 * Dane syntetyczne sklepu KawaNaKlik (APPDB, Etap I).
 * Uruchomienie: wp eval-file seed_kawanaklik.php
 * Wszystkie osoby, adresy i e-maile są fikcyjne (domena .test).
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

mt_srand( 2026 ); // Powtarzalne dane przy każdym uruchomieniu.

// --- Płatności i wysyłka -----------------------------------------------------
update_option( 'woocommerce_cod_settings', array( 'enabled' => 'yes', 'title' => 'Płatność przy odbiorze' ) );
update_option( 'woocommerce_bacs_settings', array( 'enabled' => 'yes', 'title' => 'Przelew bankowy' ) );
update_option( 'woocommerce_calc_taxes', 'no' );

$zone = new WC_Shipping_Zone();
$zone->set_zone_name( 'Polska' );
$zone->add_location( 'PL', 'country' );
$zone->save();
$instance_id = $zone->add_shipping_method( 'flat_rate' );
update_option( "woocommerce_flat_rate_{$instance_id}_settings", array( 'title' => 'Kurier', 'cost' => '14.99' ) );
$free_id = $zone->add_shipping_method( 'free_shipping' );
update_option( "woocommerce_free_shipping_{$free_id}_settings", array( 'title' => 'Darmowa dostawa', 'requires' => 'min_amount', 'min_amount' => '199' ) );

// --- Kategorie i produkty -----------------------------------------------------
$categories = array( 'Kawa ziarnista', 'Kawa mielona', 'Akcesoria', 'Zestawy prezentowe' );
$cat_ids    = array();
foreach ( $categories as $name ) {
	$term             = term_exists( $name, 'product_cat' ) ?: wp_insert_term( $name, 'product_cat' );
	$cat_ids[ $name ] = (int) $term['term_id'];
}

$products = array(
	// nazwa, kategoria, cena, stan, SKU
	array( 'Etiopia Yirgacheffe 250 g', 'Kawa ziarnista', 49.90, 42, 'KNK-ETI-250' ),
	array( 'Kolumbia Supremo 1 kg', 'Kawa ziarnista', 129.00, 18, 'KNK-KOL-1000' ),
	array( 'Brazylia Santos 500 g', 'Kawa ziarnista', 64.50, 35, 'KNK-BRA-500' ),
	array( 'Espresso Blend 1 kg', 'Kawa ziarnista', 99.00, 7, 'KNK-ESP-1000' ),
	array( 'Gwatemala Antigua mielona 250 g', 'Kawa mielona', 44.90, 26, 'KNK-GWA-250M' ),
	array( 'Bezkofeinowa Meksyk mielona 250 g', 'Kawa mielona', 46.90, 3, 'KNK-MEX-250M' ),
	array( 'Drip V60 ceramiczny', 'Akcesoria', 89.00, 12, 'KNK-V60' ),
	array( 'Młynek ręczny stalowy', 'Akcesoria', 159.00, 9, 'KNK-MLY' ),
	array( 'Filtry papierowe 100 szt.', 'Akcesoria', 19.90, 80, 'KNK-FIL-100' ),
	array( 'Zestaw degustacyjny 4 x 100 g', 'Zestawy prezentowe', 79.00, 15, 'KNK-DEG-4' ),
	array( 'Zestaw „Poranek” (kawa + kubek)', 'Zestawy prezentowe', 119.00, 0, 'KNK-POR' ),
);

$product_ids = array();
foreach ( $products as $p ) {
	$existing = wc_get_product_id_by_sku( $p[4] );
	$product  = $existing ? wc_get_product( $existing ) : new WC_Product_Simple();
	$product->set_name( $p[0] );
	$product->set_sku( $p[4] );
	$product->set_regular_price( (string) $p[2] );
	$product->set_manage_stock( true );
	$product->set_stock_quantity( $p[3] );
	$product->set_category_ids( array( $cat_ids[ $p[1] ] ) );
	$product->set_short_description( 'Produkt testowy sklepu KawaNaKlik (dane syntetyczne).' );
	$product_ids[] = $product->save();
}

// --- Klienci ------------------------------------------------------------------
$customers = array(
	array( 'Anna', 'Zielińska', 'Kraków' ),
	array( 'Piotr', 'Wiśniewski', 'Gdańsk' ),
	array( 'Kasia', 'Nowicka', 'Poznań' ),
	array( 'Tomasz', 'Lis', 'Wrocław' ),
	array( 'Ola', 'Mazur', 'Łódź' ),
	array( 'Marek', 'Dąbrowski', 'Lublin' ),
	array( 'Ewa', 'Kowalczyk', 'Warszawa' ),
	array( 'Jan', 'Sowa', 'Rzeszów' ),
);

$customer_ids = array();
foreach ( $customers as $i => $c ) {
	$email = sprintf( 'klient%02d@kawanaklik.test', $i + 1 );
	$id    = email_exists( $email );
	if ( ! $id ) {
		$id = wc_create_new_customer( $email, '', wp_generate_password( 20 ), array( 'first_name' => $c[0], 'last_name' => $c[1] ) );
	}
	$customer = new WC_Customer( $id );
	$customer->set_billing_first_name( $c[0] );
	$customer->set_billing_last_name( $c[1] );
	$customer->set_billing_city( $c[2] );
	$customer->set_billing_country( 'PL' );
	$customer->set_billing_address_1( 'ul. Testowa ' . ( $i + 1 ) );
	$customer->set_billing_postcode( sprintf( '%02d-%03d', 10 + $i * 7, 100 + $i ) );
	$customer->set_billing_email( $email );
	$customer->set_billing_phone( '500 000 ' . sprintf( '%03d', $i + 1 ) );
	$customer->save();
	$customer_ids[] = $id;
}

// --- Zamówienia (z reklamacjami, zwrotami i pytaniami w notatkach) ------------
$statuses = array( 'completed', 'completed', 'completed', 'processing', 'processing', 'on-hold', 'pending', 'cancelled', 'refunded' );
$notes    = array(
	'reklamacja' => 'Klient zgłasza reklamację: paczka dotarła uszkodzona, rozsypane ziarna.',
	'zwrot'      => 'Klient prosi o zwrot w terminie 14 dni – produkt nieotwarty.',
	'pytanie'    => 'Pytanie klienta: czy kawa jest odpowiednia do ekspresu kolbowego?',
	'opoznienie' => 'Klient pyta o status przesyłki – brak aktualizacji od 3 dni.',
);

for ( $n = 0; $n < 24; $n++ ) {
	$cid   = $customer_ids[ $n % count( $customer_ids ) ];
	$order = wc_create_order( array( 'customer_id' => $cid ) );
	$items = mt_rand( 1, 3 );
	for ( $k = 0; $k < $items; $k++ ) {
		$order->add_product( wc_get_product( $product_ids[ mt_rand( 0, count( $product_ids ) - 1 ) ] ), mt_rand( 1, 2 ) );
	}
	$customer = new WC_Customer( $cid );
	$order->set_address( $customer->get_billing(), 'billing' );
	$order->set_payment_method( 0 === $n % 2 ? 'bacs' : 'cod' );
	$order->set_payment_method_title( 0 === $n % 2 ? 'Przelew bankowy' : 'Płatność przy odbiorze' );
	$order->calculate_totals();
	$order->set_date_created( strtotime( '-' . mt_rand( 0, 30 ) . ' days -' . mt_rand( 0, 23 ) . ' hours' ) );
	$order->set_status( $statuses[ $n % count( $statuses ) ] );
	$order->save();

	if ( 0 === $n % 4 ) {
		$key = array_keys( $notes )[ ( $n / 4 ) % count( $notes ) ];
		$order->add_order_note( $notes[ $key ], 0, false );
		$order->update_meta_data( '_knk_typ_zgloszenia', $key );
		$order->save();
	}
}

WP_CLI::success( sprintf( 'Produkty: %d, klienci: %d, zamówienia: 24.', count( $product_ids ), count( $customer_ids ) ) );
