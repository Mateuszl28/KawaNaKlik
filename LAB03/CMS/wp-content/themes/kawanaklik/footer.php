<?php
/**
 * Stopka – wspólny koniec każdej strony.
 *
 * @package KawaNaKlik
 */

$kawanaklik_telefon   = kawanaklik_option( 'telefon' );
$kawanaklik_email     = kawanaklik_option( 'email' );
$kawanaklik_adres     = kawanaklik_option( 'adres' );
$kawanaklik_facebook  = kawanaklik_option( 'facebook' );
$kawanaklik_instagram = kawanaklik_option( 'instagram' );
?>
</main>
<footer class="site-footer">
	<div class="container site-footer__inner">
		<div class="site-footer__widgets">
			<div class="widget footer-contact">
				<h3 class="widget__title"><?php esc_html_e( 'Kontakt', 'kawanaklik' ); ?></h3>
				<?php if ( $kawanaklik_telefon ) : ?>
					<p>
						<a href="<?php echo esc_url( 'tel:' . preg_replace( '/[^0-9+]/', '', $kawanaklik_telefon ) ); ?>">
							<?php echo esc_html( $kawanaklik_telefon ); ?>
						</a>
					</p>
				<?php endif; ?>
				<?php if ( $kawanaklik_email ) : ?>
					<p><a href="<?php echo esc_url( 'mailto:' . $kawanaklik_email ); ?>"><?php echo esc_html( $kawanaklik_email ); ?></a></p>
				<?php endif; ?>
				<?php if ( $kawanaklik_adres ) : ?>
					<p><?php echo nl2br( esc_html( $kawanaklik_adres ) ); ?></p>
				<?php endif; ?>
				<?php if ( $kawanaklik_facebook || $kawanaklik_instagram ) : ?>
					<p class="footer-social">
						<?php if ( $kawanaklik_facebook ) : ?>
							<a href="<?php echo esc_url( $kawanaklik_facebook ); ?>" rel="noopener" target="_blank">Facebook</a>
						<?php endif; ?>
						<?php if ( $kawanaklik_instagram ) : ?>
							<a href="<?php echo esc_url( $kawanaklik_instagram ); ?>" rel="noopener" target="_blank">Instagram</a>
						<?php endif; ?>
					</p>
				<?php endif; ?>
			</div>
			<?php dynamic_sidebar( 'footer-1' ); ?>
		</div>
		<?php
		wp_nav_menu(
			array(
				'theme_location' => 'footer',
				'container'      => 'nav',
				'menu_class'     => 'footer-menu',
				'depth'          => 1,
				'fallback_cb'    => false,
			)
		);
		?>
		<p class="site-footer__copy">&copy; <?php echo esc_html( gmdate( 'Y' ) ); ?> <?php bloginfo( 'name' ); ?></p>
	</div>
</footer>
<?php wp_footer(); // OBOWIĄZKOWE – bez tego nie zadziała pasek admina ani skrypty. ?>
</body>
</html>
