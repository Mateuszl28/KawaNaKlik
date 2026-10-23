<?php
/**
 * Archiwum opinii klientów (/opinie/).
 *
 * @package KawaNaKlik
 */

get_header();
?>

<h1 class="page-title"><?php esc_html_e( 'Opinie klientów', 'kawanaklik' ); ?></h1>
<p class="archive-intro"><?php esc_html_e( 'Co mówią o nas osoby, które piją naszą kawę.', 'kawanaklik' ); ?></p>

<?php if ( have_posts() ) : ?>
	<div class="opinie__grid">
		<?php
		while ( have_posts() ) :
			the_post();
			get_template_part( 'template-parts/opinia-card' );
		endwhile;
		?>
	</div>
	<?php the_posts_pagination(); ?>
<?php else : ?>
	<p><?php esc_html_e( 'Nie ma jeszcze opinii.', 'kawanaklik' ); ?></p>
<?php endif; ?>

<?php
get_footer();
