<?php
/**
 * Pojedyncza opinia klienta.
 *
 * @package KawaNaKlik
 */

get_header();

while ( have_posts() ) :
	the_post();
	$kawanaklik_produkt = get_field( 'produkt', get_the_ID() ); // ID produktu WooCommerce.
	?>
	<div class="opinia-single">
		<p><a href="<?php echo esc_url( get_post_type_archive_link( 'opinia' ) ); ?>">← <?php esc_html_e( 'Wszystkie opinie', 'kawanaklik' ); ?></a></p>
		<?php get_template_part( 'template-parts/opinia-card' ); ?>
		<?php if ( $kawanaklik_produkt ) : ?>
			<p class="opinia-single__product">
				<?php esc_html_e( 'Opinia o produkcie:', 'kawanaklik' ); ?>
				<a href="<?php echo esc_url( get_permalink( $kawanaklik_produkt ) ); ?>"><?php echo esc_html( get_the_title( $kawanaklik_produkt ) ); ?></a>
			</p>
		<?php endif; ?>
	</div>
	<?php
endwhile;

get_footer();
