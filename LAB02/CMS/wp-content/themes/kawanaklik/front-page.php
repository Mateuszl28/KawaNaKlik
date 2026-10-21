<?php
/**
 * Strona główna. Główne zapytanie dotyczy samej strony ustawionej jako
 * „Strona główna”; ostatnie wpisy pobieramy dodatkowym WP_Query.
 *
 * @package KawaNaKlik
 */

get_header();
?>

<?php
while ( have_posts() ) :
	the_post();
	?>
	<section class="hero">
		<h1 class="hero__title"><?php the_title(); ?></h1>
		<div class="hero__text"><?php the_content(); ?></div>
		<a class="button" href="<?php echo esc_url( home_url( '/sklep/' ) ); ?>"><?php esc_html_e( 'Przejdź do sklepu', 'kawanaklik' ); ?></a>
	</section>
	<?php
endwhile;
?>

<section class="latest">
	<h2 class="section-title"><?php esc_html_e( 'Z bloga', 'kawanaklik' ); ?></h2>
	<div class="cards cards--3">
		<?php
		$kawanaklik_latest = new WP_Query(
			array(
				'post_type'           => 'post',
				'posts_per_page'      => 3,
				'ignore_sticky_posts' => true,
				'no_found_rows'       => true, // Nie liczymy stron – szybsze zapytanie.
			)
		);
		while ( $kawanaklik_latest->have_posts() ) :
			$kawanaklik_latest->the_post();
			get_template_part( 'template-parts/content' );
		endwhile;
		wp_reset_postdata(); // Przywraca globalny $post – zawsze po własnym WP_Query!
		?>
	</div>
</section>

<p class="front-note">
	<?php
	/* translators: %s: tytuł strony głównej */
	printf( esc_html__( 'Jesteś na stronie: %s', 'kawanaklik' ), '<strong>' . esc_html( get_the_title() ) . '</strong>' );
	?>
</p>

<?php
get_footer();
