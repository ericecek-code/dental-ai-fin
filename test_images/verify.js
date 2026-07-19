(async () => {
  // Najdi canvas a nastav imageUrl umelo (nespustime upload)
  // Simulujeme fullscreen otvorenie cez test: nastavime image src urobene z backendu
  const overlayImg = document.querySelector('img[alt="RTG snímka"]');
  const overlayBtn = document.querySelector('button[aria-label="Zväčšiť na celú obrazovku"]');
  return JSON.stringify({
    hasOverlayImg: !!overlayImg,
    hasOverlayBtn: !!overlayBtn,
    translationsBody: document.body.innerText.includes('Kaz') || document.body.innerText.includes('Korunka'),
    slovakUI: document.body.innerText.includes('Prah spoľahlivosti'),
  });
})()
