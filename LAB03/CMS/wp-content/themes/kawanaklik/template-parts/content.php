<?php
/**
 * Karta wpisu na listach (blog, archiwa, strona główna).
 *
 * @package KawaNaKlik
 */

?>
<article <?php post_class( 'card' ); ?>>
	<?php if ( has_post_thumbnail() ) : ?>
		<a class="card__thumb" href="<?php the_permalink(); ?>"><?php the_post_thumbnail( 'medium' ); ?></a>
	<?php endif; ?>
	<div class="card__body">
		<p class="card__date"><?php echo esc_html( get_the_date() ); ?></p>
		<h2 class="card__title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
		<?php the_excerpt(); ?>
		<a class="card__more" href="<?php the_permalink(); ?>"><?php esc_html_e( 'Czytaj dalej', 'kawanaklik' ); ?> →</a>
	</div>
</article>
