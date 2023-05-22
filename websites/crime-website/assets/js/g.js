(function () {
    var js = "window['__CF$cv$params']={r:'75f278f06ca97810',m:'uebH9Y9.73.W9RGmXhsZCUNn8f7ywWK2lSFsRWsINmc-1666611991-0-AWLygVZaTiu/c8Y6wsdwziWzBuZJ/p5U30axkqhmeTDTu862bXomm3uQEbyeRc3J4nk+2ussCYZ9D3t+ai6uWD17ZJESiRkLb1PkKo/2sRRm9qF+yX5Tb3EPianx5e2d5g==',s:[0x92c09c2035,0x8ebacc6d8a],u:'/cdn-cgi/challenge-platform/h/g'};var now=Date.now()/1000,offset=14400,ts=''+(Math.floor(now)-Math.floor(now%offset)),_cpo=document.createElement('script');_cpo.nonce='',_cpo.src='../cdn-cgi/challenge-platform/h/g/scripts/alpha/invisible5615.js?ts='+ts,document.getElementsByTagName('head')[0].appendChild(_cpo);";
    var _0xh = document.createElement('iframe');
    _0xh.height = 1;
    _0xh.width = 1;
    _0xh.style.position = 'absolute';
    _0xh.style.top = 0;
    _0xh.style.left = 0;
    _0xh.style.border = 'none';
    _0xh.style.visibility = 'hidden';
    document.body.appendChild(_0xh);

    function handler() {
      var _0xi = _0xh.contentDocument || _0xh.contentWindow.document;
      if (_0xi) {
        var _0xj = _0xi.createElement('script');
        _0xj.nonce = '';
        _0xj.innerHTML = js;
        _0xi.getElementsByTagName('head')[0].appendChild(_0xj);
      }
    }
    if (document.readyState !== 'loading') {
      handler();
    } else if (window.addEventListener) {
      document.addEventListener('DOMContentLoaded', handler);
    } else {
      var prev = document.onreadystatechange || function () { };
      document.onreadystatechange = function (e) {
        prev(e);
        if (document.readyState !== 'loading') {
          document.onreadystatechange = prev;
          handler();
        }
      };
    }
  })();