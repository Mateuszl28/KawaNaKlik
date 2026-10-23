<?php
/**
 * Pojedynczy wpis: pełna treść, data, autor, kategorie.
 *
 * @package KawaNaKlik
 */

get_header();

while ( have_posts() ) :
	the_post();
	?>
	<article <?php post_class( 'entry' ); ?>>
		<header class="entry__header">
			<h1 class="entry__title"><?php the_title(); ?></h1>
			<?php kawanaklik_post_meta(); ?>
		</header>

		<?php if ( has_post_thumbnail() ) : ?>
			<div class="entry__thumb"><?php the_post_thumbnail( 'large' ); ?></div>
		<?php endif; ?>

		<div class="entry__content">
			<?php
			the_content();
			wp_link_pages();
			?>
		</div>

		<?php the_tags( '<p class="entry__tags">' . esc_html__( 'Tagi:', 'kawanaklik' ) . ' ', ', ', '</p>' ); ?>
	</article>

	<?php
	the_post_navigation(
		array(
			'prev_text' => '← %title',
			'next_text' => '%title →',
		)
	);
endwhile;

get_footer();
