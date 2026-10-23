<?php
/**
 * Szablon awaryjny – obsługuje każdy widok, dla którego nie ma bardziej
 * szczegółowego pliku (blog, archiwa, wyszukiwanie, strony WooCommerce).
 *
 * @package KawaNaKlik
 */

get_header();
?>

<?php if ( is_home() && ! is_front_page() ) : ?>
	<h1 class="page-title"><?php single_post_title(); ?></h1>
<?php elseif ( is_archive() ) : ?>
	<?php the_archive_title( '<h1 class="page-title">', '</h1>' ); ?>
<?php elseif ( is_search() ) : ?>
	<h1 class="page-title">
		<?php
		/* translators: %s: szukana fraza */
		printf( esc_html__( 'Wyniki wyszukiwania: %s', 'kawanaklik' ), '<span>' . esc_html( get_search_query() ) . '</span>' );
		?>
	</h1>
<?php endif; ?>

<?php if ( have_posts() ) : ?>
	<div class="cards">
		<?php
		while ( have_posts() ) :
			the_post();
			get_template_part( 'template-parts/content', get_post_type() );
		endwhile;
		?>
	</div>
	<?php the_posts_pagination(); ?>
<?php else : ?>
	<p><?php esc_html_e( 'Brak treści.', 'kawanaklik' ); ?></p>
<?php endif; ?>

<?php
get_footer();
