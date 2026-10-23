<?php
/**
 * Blok Opinie klientów – pobiera wpisy typu „opinia” własnym WP_Query.
 *
 * @package KawaNaKlik
 */

$title      = get_field( 'title' );
$count      = (int) get_field( 'count' );
$min_rating = (int) get_field( 'min_rating' );
$id         = ! empty( $block['anchor'] ) ? $block['anchor'] : 'opinie-' . $block['id'];

$args = array(
	'post_type'      => 'opinia',
	'posts_per_page' => $count > 0 ? $count : 3,
	'no_found_rows'  => true,
);
if ( $min_rating > 1 ) {
	$args['meta_query'] = array( // phpcs:ignore WordPress.DB.SlowDBQuery.slow_db_query_meta_query
		array(
			'key'     => 'ocena',
			'value'   => $min_rating,
			'compare' => '>=',
			'type'    => 'NUMERIC',
		),
	);
}
$opinie = new WP_Query( $args );
?>
<section id="<?php echo esc_attr( $id ); ?>" class="opinie">
	<?php if ( $title ) : ?>
		<h2 class="section-title"><?php echo esc_html( $title ); ?></h2>
	<?php endif; ?>

	<?php if ( $opinie->have_posts() ) : ?>
		<div class="opinie__grid">
			<?php
			while ( $opinie->have_posts() ) :
				$opinie->the_post();
				get_template_part( 'template-parts/opinia-card' );
			endwhile;
			wp_reset_postdata(); // Przywraca globalny $post po własnym WP_Query.
			?>
		</div>
		<p class="opinie__more"><a href="<?php echo esc_url( get_post_type_archive_link( 'opinia' ) ); ?>"><?php esc_html_e( 'Wszystkie opinie →', 'kawanaklik' ); ?></a></p>
	<?php elseif ( $is_preview ) : ?>
		<p><em><?php esc_html_e( 'Brak opinii – dodaj je w menu Opinie.', 'kawanaklik' ); ?></em></p>
	<?php endif; ?>
</section>
