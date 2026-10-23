<?php
/**
 * Blok Przewagi (USP) – cztery kafelki. Każdy kafelek to pole Grupa
 * (ikona, tytuł, opis) – w ACF Free nie ma pola Repeater.
 *
 * @package KawaNaKlik
 */

$title = get_field( 'title' );
$items = array();
for ( $i = 1; $i <= 4; $i++ ) {
	$item = get_field( "usp_{$i}" );
	if ( ! empty( $item['title'] ) ) {
		$items[] = $item;
	}
}
$id = ! empty( $block['anchor'] ) ? $block['anchor'] : 'usp-' . $block['id'];
?>
<section id="<?php echo esc_attr( $id ); ?>" class="usp">
	<?php if ( $title ) : ?>
		<h2 class="section-title"><?php echo esc_html( $title ); ?></h2>
	<?php endif; ?>

	<?php if ( $items ) : ?>
		<div class="usp__grid">
			<?php foreach ( $items as $item ) : ?>
				<div class="usp__item">
					<?php if ( ! empty( $item['icon'] ) ) : ?>
						<span class="usp__icon" aria-hidden="true"><?php echo esc_html( $item['icon'] ); ?></span>
					<?php endif; ?>
					<h3 class="usp__title"><?php echo esc_html( $item['title'] ); ?></h3>
					<?php if ( ! empty( $item['text'] ) ) : ?>
						<p class="usp__text"><?php echo esc_html( $item['text'] ); ?></p>
					<?php endif; ?>
				</div>
			<?php endforeach; ?>
		</div>
	<?php elseif ( $is_preview ) : ?>
		<p><em><?php esc_html_e( 'Uzupełnij przewagi w panelu bloku →', 'kawanaklik' ); ?></em></p>
	<?php endif; ?>
</section>
