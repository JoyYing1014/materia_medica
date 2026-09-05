(function () {
  'use strict';

  var menuButton = document.querySelector('.cs-menu-button');
  var navLinks = document.querySelector('.cs-nav__links');

  if (menuButton && navLinks) {
    menuButton.addEventListener('click', function () {
      var isOpen = menuButton.getAttribute('aria-expanded') === 'true';
      menuButton.setAttribute('aria-expanded', String(!isOpen));
      navLinks.classList.toggle('cs-nav__links--open', !isOpen);
    });

    navLinks.addEventListener('click', function (event) {
      if (event.target.tagName === 'A') {
        menuButton.setAttribute('aria-expanded', 'false');
        navLinks.classList.remove('cs-nav__links--open');
      }
    });
  }

  var revealItems = document.querySelectorAll('.cs-reveal');
  if (!('IntersectionObserver' in window)) {
    revealItems.forEach(function (item) { item.classList.add('cs-visible'); });
    return;
  }

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('cs-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08 });

  revealItems.forEach(function (item) { observer.observe(item); });
}());
