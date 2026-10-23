<?php
/**
 * Karta opinii – używana w bloku „Opinie”, archiwum i widoku pojedynczym.
 *
 * @package KawaNaKlik
 */

// ID podajemy jawnie: wewnątrz bloku ACF get_field() bez ID czyta pola bloku, a nie wpisu z pętli.
$kawanaklik_ocena  = (int) get_field( 'ocena', get_the_ID() );
$kawanaklik_miasto = get_field( 'miasto', get_the_ID() );
?>
<article <?php post_class( 'opinia-card' ); ?>>
	<?php if ( $kawanaklik_ocena ) : ?>
		<p class="opinia-card__stars" aria-label="<?php echo esc_attr( sprintf( /* translators: %d: ocena */ __( 'Ocena %d na 5', 'kawanaklik' ), $kawanaklik_ocena ) ); ?>">
			<?php echo esc_html( str_repeat( '★', $kawanaklik_ocena ) . str_repeat( '☆', 5 - $kawanaklik_ocena ) ); ?>
		</p>
	<?php endif; ?>
	<blockquote class="opinia-card__text"><?php echo wp_kses_post( wpautop( get_the_content() ) ); ?></blockquote>
	<p class="opinia-card__author">
		<a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
		<?php if ( $kawanaklik_miasto ) : ?>
			<span class="opinia-card__city">· <?php echo esc_html( $kawanaklik_miasto ); ?></span>
		<?php endif; ?>
	</p>
</article>
