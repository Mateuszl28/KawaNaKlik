<?php
/**
 * Blok „Z bloga” – ostatnie wpisy pobrane własnym WP_Query.
 *
 * @package KawaNaKlik
 */

$title = get_field( 'title' );
$count = (int) get_field( 'count' );
$id    = ! empty( $block['anchor'] ) ? $block['anchor'] : 'blog-' . $block['id'];

$latest = new WP_Query(
	array(
		'post_type'           => 'post',
		'posts_per_page'      => $count > 0 ? $count : 3,
		'ignore_sticky_posts' => true,
		'no_found_rows'       => true,
	)
);
?>
<section id="<?php echo esc_attr( $id ); ?>" class="latest">
	<?php if ( $title ) : ?>
		<h2 class="section-title"><?php echo esc_html( $title ); ?></h2>
	<?php endif; ?>
	<div class="cards cards--3">
		<?php
		while ( $latest->have_posts() ) :
			$latest->the_post();
			get_template_part( 'template-parts/content' );
		endwhile;
		wp_reset_postdata(); // Przywraca globalny $post – zawsze po własnym WP_Query!
		?>
	</div>
</section>
