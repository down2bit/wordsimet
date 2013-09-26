// This script searches the page for an element with id="new-section-redirect"
// that contains a link to a URL of the form
//      http://en.wiktionary.org/w/index.php?title=...&action=edit&section=new
// and, if it finds one, then it modifies the page's new-section-link (the "+"
// tab) to point to that URL. Thus, for example, the new-section-link at
// [[Wiktionary:Grease pit]] will add a new section to the Grease pit's current
// monthly subpage, rather than to the Grease pit itself.

addOnloadHook
(
  function ()
  {
    var regexp =
      /^(?:https?:)?[/][/]en[.]wiktionary[.]org[/]w[/]index[.]php[?]title=[^&]+&action=edit&section=new$/;

    var urlForNewSectionLink = $('#new-section-redirect a').prop('href');

    if(! urlForNewSectionLink || ! regexp.test(urlForNewSectionLink))
      return;

    if($('#ca-addsection').length == 0)
      // If we don't have an "add new section" link, e.g. because the current
      // page is protected, then we should add one:
      $('#ca-history').before
      (
        newNode
        (
          'li',
          { 'id': 'ca-addsection', 'class': 'collapsible' },
          newNode
          (
            'span', // not sure why Vector has a stray <span> here
            newNode
            (
              'a',
              {
                'href': urlForNewSectionLink,
                'title': 'Start a new section [+]',
                'accesskey': '+'
              },
              '\xA0+\xA0'
            )
          )
        )
      );
    else
      $('#ca-addsection a').prop('href', urlForNewSectionLink);

    $('#new-section-redirect.hide-when-done').css('display', 'none');
  }
);