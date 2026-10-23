<?php
/**
 * Blok FAQ – pytania z typu treści „faq” (ACF Free nie ma pola Repeater)
 * oraz dane strukturalne FAQPage w JSON-LD dla Google.
 *
 * @package KawaNaKlik
 */

$title = get_field( 'title' );
$count = (int) get_field( 'count' );
$id    = ! empty( $block['anchor'] ) ? $block['anchor'] : 'faq-' . $block['id'];

$pytania = get_posts(
	array(
		'post_type'      => 'faq',
		'posts_per_page' => $count > 0 ? $count : 5,
		'orderby'        => array(
			'menu_order' => 'ASC',
			'date'       => 'ASC',
		),
	)
);
?>
<section id="<?php echo esc_attr( $id ); ?>" class="faq">
	<?php if ( $title ) : ?>
		<h2 class="section-title"><?php echo esc_html( $title ); ?></h2>
	<?php endif; ?>

	<?php if ( $pytania ) : ?>
		<div class="faq__list">
			<?php foreach ( $pytania as $pytanie ) : ?>
				<details class="faq__item">
					<summary class="faq__question"><?php echo esc_html( get_the_title( $pytanie ) ); ?></summary>
					<div class="faq__answer"><?php echo wp_kses_post( wpautop( $pytanie->post_content ) ); ?></div>
				</details>
			<?php endforeach; ?>
		</div>

		<?php
		if ( ! $is_preview ) :
			$schema = array(
				'@context'   => 'https://schema.org',
				'@type'      => 'FAQPage',
				'mainEntity' => array_map(
					static fn( $pytanie ) => array(
						'@type'          => 'Question',
						'name'           => wp_strip_all_tags( get_the_title( $pytanie ) ),
						'acceptedAnswer' => array(
							'@type' => 'Answer',
							'text'  => wp_strip_all_tags( $pytanie->post_content ),
						),
					),
					$pytania
				),
			);
			// wp_json_encode z JSON_HEX_TAG zamienia < i > na </> – treść nie zamknie znacznika <script>.
			?>
			<script type="application/ld+json"><?php echo wp_json_encode( $schema, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_HEX_TAG ); ?></script>
		<?php endif; ?>
	<?php elseif ( $is_preview ) : ?>
		<p><em><?php esc_html_e( 'Brak pytań – dodaj je w menu FAQ.', 'kawanaklik' ); ?></em></p>
	<?php endif; ?>
</section>
