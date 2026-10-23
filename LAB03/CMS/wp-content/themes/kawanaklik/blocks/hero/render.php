<?php
/**
 * Blok Hero.
 * ACF przekazuje: $block (ustawienia bloku), $is_preview (podgląd w edytorze).
 *
 * @package KawaNaKlik
 */

$title  = get_field( 'title' );
$text   = get_field( 'text' );
$image  = get_field( 'image' );   // ID załącznika.
$button = get_field( 'button' );  // Tablica: url, title, target.
$id     = ! empty( $block['anchor'] ) ? $block['anchor'] : 'hero-' . $block['id'];
?>
<section id="<?php echo esc_attr( $id ); ?>" class="hero<?php echo $image ? ' hero--image' : ''; ?>">
	<?php if ( $image ) : ?>
		<?php echo wp_get_attachment_image( $image, 'full', false, array( 'class' => 'hero__bg' ) ); ?>
	<?php endif; ?>
	<div class="hero__content">
		<?php if ( $title ) : ?>
			<h1 class="hero__title"><?php echo esc_html( $title ); ?></h1>
		<?php elseif ( $is_preview ) : ?>
			<p><em><?php esc_html_e( 'Uzupełnij tytuł w panelu bloku →', 'kawanaklik' ); ?></em></p>
		<?php endif; ?>

		<?php if ( $text ) : ?>
			<p class="hero__text"><?php echo esc_html( $text ); ?></p>
		<?php endif; ?>

		<?php if ( $button ) : ?>
			<a class="button" href="<?php echo esc_url( $button['url'] ); ?>"
				target="<?php echo esc_attr( $button['target'] ? $button['target'] : '_self' ); ?>">
				<?php echo esc_html( $button['title'] ); ?>
			</a>
		<?php endif; ?>
	</div>
</section>
