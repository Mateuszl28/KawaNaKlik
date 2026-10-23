<?php
/**
 * Nagłówek – wspólny początek każdej strony.
 *
 * @package KawaNaKlik
 */

?>
<!doctype html>
<html <?php language_attributes(); ?>>
<head>
	<meta charset="<?php bloginfo( 'charset' ); ?>">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<?php wp_head(); // Tu WordPress i pluginy wstawiają CSS, meta i skrypty – OBOWIĄZKOWE. ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<?php $kawanaklik_promo = kawanaklik_option( 'promo' ); ?>
<?php if ( $kawanaklik_promo ) : ?>
	<div class="promo-bar"><?php echo esc_html( $kawanaklik_promo ); ?></div>
<?php endif; ?>
<header class="site-header">
	<div class="container site-header__inner">
		<a class="site-logo" href="<?php echo esc_url( home_url( '/' ) ); ?>">
			<?php bloginfo( 'name' ); ?>
		</a>
		<button class="nav-toggle" aria-controls="primary-menu" aria-expanded="false">
			<?php esc_html_e( 'Menu', 'kawanaklik' ); ?>
		</button>
		<?php
		wp_nav_menu(
			array(
				'theme_location' => 'primary',
				'container'      => 'nav',
				'menu_id'        => 'primary-menu',
				'fallback_cb'    => false,
			)
		);
		?>
	</div>
</header>
<main class="site-main container">
