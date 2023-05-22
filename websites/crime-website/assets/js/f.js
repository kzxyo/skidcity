













(this.webpackJsonpembedbuilder = this.webpackJsonpembedbuilder || []).push([[0], {
    193: function (e, t, n) { },
    194: function (e, t, n) {
        "use strict";
        n.r(t);
        var a = n(0),
            l = n.n(a),
            r = n(73),
            o = n.n(r),
            c = (n(84), n(3)),
            i = n(4),
            u = n(6),
            d = n(5),
            m = function (e) {
                Object(u.a)(n, e);
                var t = Object(d.a)(n);

                function n(e) {
                    var a;
                    return Object(c.a)(this, n), (a = t.call(this, e)).state = {
                        content: ""
                    }, a
                }
                return Object(i.a)(n, [{
                    key: "updateContent",
                    value: function (e) {
                        this.setState({
                            content: e.target.value
                        })
                    }
                }, {
                    key: "render",
                    value: function () {
                        var e = this;
                        return l.a.createElement("div", {
                            className: "embed-group embed-content"
                        }, l.a.createElement("textarea", {
                            name: "content",
                            placeholder: "Content",
                            maxLength: "2000",
                            value: this.state.content,
                            onChange: function (t) {
                                return e.updateContent(t)
                            }
                        }))
                    }
                }]), n
            }(l.a.Component),
            s = function (e) {
                Object(u.a)(n, e);
                var t = Object(d.a)(n);

                function n(e) {
                    var a;
                    return Object(c.a)(this, n), (a = t.call(this, e)).state = {
                        autodelete: ""
                    }, a
                }
                return Object(i.a)(n, [{
                    key: "updateAutodelete",
                    value: function (e) {
                        this.setState({
                            autodelete: e.target.value
                        })
                    }
                }, {
                    key: "render",
                    value: function () {
                        var e = this;
                        return l.a.createElement("div", {
                            className: "embed-group embed-autodelete"
                        }, l.a.createElement("textarea", {
                            name: "autodelete",
                            placeholder: "Autodelete",
                            maxLength: "2000",
                            value: this.state.autodelete,
                            onChange: function (t) {
                                return e.updateAutodelete(t)
                            }
                        }))
                    }
                }]), n
            }(l.a.Component),
            v = n(78),
            b = function (e) {
                Object(u.a)(n, e);
                var t = Object(d.a)(n);

                function n(e) {
                    var a;
                    return Object(c.a)(this, n), (a = t.call(this, e)).handleClick = function () {
                        a.setState({
                            displayColorPicker: !a.state.displayColorPicker
                        })
                    }, a.handleClose = function () {
                        a.setState({
                            displayColorPicker: !1
                        })
                    }, a.handleChangeComplete = function (e, t) {
                        a.setState({
                            color: e.hex,
                            intColor: 65536 * Math.round(e.rgb.r) + 256 * Math.round(e.rgb.g) + Math.round(e.rgb.b)
                        }), document.getElementById("builder-container").style["border-left"] = "5px solid ".concat(e.hex)
                    }, a.state = {
                        color: "#4f545c",
                        intColor: 0,
                        displayColorPicker: !1
                    }, a
                }
                return Object(i.a)(n, [{
                    key: "render",
                    value: function () {
                        return l.a.createElement("div", {
                            className: "embed-group embed-color"
                        }, l.a.createElement("input", {
                            id: "color",
                            type: "text",
                            name: "color",
                            placeholder: "Embed Color",
                            value: this.state.intColor,
                            onClick: this.handleClick,
                            style: {
                                cursor: "pointer"
                            },
                            readOnly: !0
                        }), this.state.displayColorPicker ? l.a.createElement("div", {
                            style: {
                                position: "absolute",
                                zIndex: 2
                            }
                        }, l.a.createElement("div", {
                            style: {
                                position: "fixed",
                                top: "0px",
                                right: "0px",
                                bottom: "0px",
                                left: "0px",
                                backgroundColor: "rgba(0, 0, 0, .15)"
                            },
                            onClick: this.handleClose
                        }), l.a.createElement(v.a, {
                            color: this.state.color,
                            disableAlpha: !0,
                            onChangeComplete: this.handleChangeComplete
                        })) : null)
                    }
                }]), n
            }(l.a.Component),
            h = function (e) {
                Object(u.a)(n, e);
                var t = Object(d.a)(n);

                function n(e) {
                    var a;
                    return Object(c.a)(this, n), (a = t.call(this, e)).state = {
                        name: "",
                        URL: "",
                        iconURL: ""
                    }, a
                }
                return Object(i.a)(n, [{
                    key: "updateName",
                    value: function (e) {
                        this.setState({
                            name: e.target.value
                        })
                    }
                }, {
                    key: "updateURL",
                    value: function (e) {
                        this.setState({
                            URL: e.target.value
                        })
                    }
                }, {
                    key: "updateIconURL",
                    value: function (e) {
                        this.setState({
                            iconURL: e.target.value
                        })
                    }
                }, {
                    key: "render",
                    value: function () {
                        var e = this;
                        return l.a.createElement("div", {
                            className: "embed-group embed-author"
                        }, l.a.createElement("div", {
                            className: "embed-author-icon"
                        }, l.a.createElement("input", {
                            type: "url",
                            name: "author:icon_url",
                            placeholder: "Author Icon URL",
                            value: this.state.iconURL,
                            onChange: function (t) {
                                return e.updateIconURL(t)
                            }
                        })), l.a.createElement("div", {
                            className: "embed-author-name"
                        }, l.a.createElement("input", {
                            type: "text",
                            name: "author:name",
                            placeholder: "Author Name",
                            maxLength: "256",
                            value: this.state.name,
                            onChange: function (t) {
                                return e.updateName(t)
                            }
                        })), l.a.createElement("div", {
                            className: "embed-author-url"
                        }, l.a.createElement("input", {
                            type: "url",
                            name: "author:url",
                            placeholder: "Author URL",
                            value: this.state.URL,
                            onChange: function (t) {
                                return e.updateURL(t)
                            }
                        })))
                    }
                }]), n
            }(l.a.Component),
            p = function (e) {
                Object(u.a)(n, e);
                var t = Object(d.a)(n);

                function n(e) {
                    var a;
                    return Object(c.a)(this, n), (a = t.call(this, e)).state = {
                        title: "",
                        URL: ""
                    }, a
                }
                return Object(i.a)(n, [{
                    key: "updateTitle",
                    value: function (e) {
                        this.setState({
                            title: e.target.value
                        })
                    }
                }, {
                    key: "updateURL",
                    value: function (e) {
                        this.setState({
                            URL: e.target.value
                        })
                    }
                }, {
                    key: "render",
                    value: function () {
                        var e = this;
                        return l.a.createElement("div", {
                            className: "embed-group embed-title"
                        }, l.a.createElement("div", {
                            className: "embed-title-text"
                        }, l.a.createElement("input", {
                            type: "text",
                            name: "title",
                            placeholder: "Title",
                            maxLength: "256",
                            value: this.state.title,
                            onChange: function (t) {
                                return e.updateTitle(t)
                            }
                        })), l.a.createElement("div", {
                            className: "embed-title-url"
                        }, l.a.createElement("input", {
                            type: "url",
                            name: "url",
                            placeholder: "URL",
                            value: this.state.URL,
                            onChange: function (t) {
                                return e.updateURL(t)
                            }
                        })))
                    }
                }]), n
            }(l.a.Component),
            f = function (e) {
                Object(u.a)(n, e);
                var t = Object(d.a)(n);

                function n(e) {
                    var a;
                    return Object(c.a)(this, n), (a = t.call(this, e)).state = {
                        description: ""
                    }, a
                }
                return Object(i.a)(n, [{
                    key: "updateDescription",
                    value: function (e) {
                        this.setState({
                            description: e.target.value
                        })
                    }
                }, {
                    key: "render",
                    value: function () {
                        var e = this;
                        return l.a.createElement("div", {
                            className: "embed-group embed-description"
                        }, l.a.createElement("textarea", {
                            name: "description",
                            placeholder: "Description",
                            maxLength: "2000",
                            rows: "5",
                            value: this.state.description,
                            onChange: function (t) {
                                return e.updateDescription(t)
                            }
                        }))
                    }
                }]), n
            }(l.a.Component),
            g = function (e) {
                Object(u.a)(n, e);
                var t = Object(d.a)(n);

                function n(e) {
                    var a;
                    return Object(c.a)(this, n), (a = t.call(this, e)).state = {
                        thumbnailURL: ""
                    }, a
                }
                return Object(i.a)(n, [{
                    key: "updateThumbnailURL",
                    value: function (e) {
                        this.setState({
                            thumbnailURL: e.target.value
                        })
                    }
                }, {
                    key: "render",
                    value: function () {
                        var e = this;
                        return l.a.createElement("div", {
                            className: "embed-group embed-thumbnail"
                        }, l.a.createElement("div", {
                            className: "embed-thumbnail-url"
                        }, l.a.createElement("input", {
                            type: "url",
                            name: "thumbnail:url",
                            placeholder: "Thumbnail URL",
                            value: this.state.thumbnailURL,
                            onChange: function (t) {
                                return e.updateThumbnailURL(t)
                            }
                        })))
                    }
                }]), n
            }(l.a.Component),
            E = function (e) {
                Object(u.a)(n, e);
                var t = Object(d.a)(n);

                function n() {
                    return Object(c.a)(this, n), t.apply(this, arguments)
                }
                return Object(i.a)(n, [{
                    key: "addField",
                    value: function (e) {
                        var t = document.getElementById("fields"),
                            n = t.children.length;
                        n >= 24 ? e.setAttribute("disabled", !0) : e.removeAttribute("disabled"), t.insertAdjacentHTML("beforeend", '<div id="field-'.concat(n, '" class="embed-group" style="display: inline-block; margin-top: 0; width: 50%">\n         <div class="field">\n           <input type="text" name="field-').concat(n, ':name" maxlength="256" placeholder="Field ').concat(n + 1, ' Name" />\n           <textarea name="field-').concat(n, ':value" maxlength="1024" rows="2" placeholder="Field ').concat(n + 1, ' Description"></textarea>\n           <label>\n             <input type="checkbox" name="field-').concat(n, ":inline\" onChange=\"let field = document.getElementById(this.name.replace(':inline', '')); this.checked ? field.setAttribute('style', 'display: inline-block; margin-top: 0; width: 50%;') : field.removeAttribute('style')\"} checked />\n             <span>Inline</span>\n           </label>\n         </div>\n       </div>")), document.getElementById("btn-removeField").removeAttribute("disabled")
                    }
                }, {
                    key: "removeField",
                    value: function (e) {
                        var t = document.getElementById("fields").children.length;
                        t - 1 ? e.removeAttribute("disabled") : e.setAttribute("disabled", !0);
                        var n = document.getElementById("field-".concat(t - 1));
                        n && n.parentNode.removeChild(n), document.getElementById("btn-addField").removeAttribute("disabled")
                    }
                }, {
                    key: "render",
                    value: function () {
                        var e = this;
                        return l.a.createElement("div", {
                            className: "embed-group embed-fields"
                        }, l.a.createElement("div", {
                            id: "fields"
                        }), l.a.createElement("div", {
                            className: "embed-group-controls"
                        }, l.a.createElement("button", {
                            id: "btn-addField",
                            type: "button",
                            onClick: function (t) {
                                return e.addField(t.target)
                            }
                        }, l.a.createElement("span", {
                            role: "img",
                            "aria-label": "Add Emoji"
                        }, "\u2795"), "\u2002 Add Field"), l.a.createElement("button", {
                            id: "btn-removeField",
                            type: "button",
                            onClick: function (t) {
                                return e.removeField(t.target)
                            }
                        }, l.a.createElement("span", {
                            role: "img",
                            "aria-label": "Remove Emoji"
                        }, "\u2796"), "\u2002 Remove Field")))
                    }
                }]), n
            }(l.a.Component),
            y = function (e) {
                Object(u.a)(n, e);
                var t = Object(d.a)(n);

                function n() {
                    return Object(c.a)(this, n), t.apply(this, arguments)
                }
                return Object(i.a)(n, [{
                    key: "addButton",
                    value: function (e) {
                        var t = document.getElementById("buttons"),
                            n = t.children.length;
                        n >= 24 ? e.setAttribute("disabled", !0) : e.removeAttribute("disabled"), t.insertAdjacentHTML("beforeend", '<div id="button-'.concat(n, '" class="embed-group" style="display: inline-block; margin-top: 0; width: 50%">\n         <div class="button">\n           <input type="text" name="button-').concat(n, ':label" maxlength="80" placeholder="Button ').concat(n + 1, ' Label" />\n           <textarea name="button-').concat(n, ':url" maxlength="1024" rows="2" placeholder="Button ').concat(n + 1, ' URL"></textarea>\n         </div>\n       </div>')), document.getElementById("btn-removeField").removeAttribute("disabled")
                    }
                }, {
                    key: "removeButton",
                    value: function (e) {
                        var t = document.getElementById("buttons").children.length;
                        t - 1 ? e.removeAttribute("disabled") : e.setAttribute("disabled", !0);
                        var n = document.getElementById("button-".concat(t - 1));
                        n && n.parentNode.removeChild(n), document.getElementById("btn-addButton").removeAttribute("disabled")
                    }
                }, {
                    key: "render",
                    value: function () {
                        var e = this;
                        return l.a.createElement("div", {
                            className: "embed-group embed-buttons"
                        }, l.a.createElement("div", {
                            id: "buttons"
                        }), l.a.createElement("div", {
                            className: "embed-group-controls"
                        }, l.a.createElement("button", {
                            id: "btn-addButton",
                            type: "button",
                            onClick: function (t) {
                                return e.addButton(t.target)
                            }
                        }, l.a.createElement("span", {
                            role: "img",
                            "aria-label": "Add Emoji"
                        }, "\u2795"), "\u2002 Add Button"), l.a.createElement("button", {
                            id: "btn-removeButton",
                            type: "button",
                            onClick: function (t) {
                                return e.removeButton(t.target)
                            }
                        }, l.a.createElement("span", {
                            role: "img",
                            "aria-label": "Remove Emoji"
                        }, "\u2796"), "\u2002 Remove Button")))
                    }
                }]), n
            }(l.a.Component),
            j = function (e) {
                Object(u.a)(n, e);
                var t = Object(d.a)(n);

                function n(e) {
                    var a;
                    return Object(c.a)(this, n), (a = t.call(this, e)).state = {
                        imageURL: ""
                    }, a
                }
                return Object(i.a)(n, [{
                    key: "updateImageURL",
                    value: function (e) {
                        this.setState({
                            imageURL: e.target.value
                        })
                    }
                }, {
                    key: "render",
                    value: function () {
                        var e = this;
                        return l.a.createElement("div", {
                            className: "embed-group embed-image"
                        }, l.a.createElement("div", {
                            className: "embed-image-url"
                        }, l.a.createElement("input", {
                            type: "url",
                            name: "image:url",
                            placeholder: "Image URL",
                            value: this.state.imageURL,
                            onChange: function (t) {
                                return e.updateImageURL(t)
                            }
                        })))
                    }
                }]), n
            }(l.a.Component),
            k = function (e) {
                Object(u.a)(n, e);
                var t = Object(d.a)(n);

                function n(e) {
                    var a;
                    return Object(c.a)(this, n), (a = t.call(this, e)).state = {
                        text: "",
                        iconURL: ""
                    }, a
                }
                return Object(i.a)(n, [{
                    key: "updateText",
                    value: function (e) {
                        this.setState({
                            text: e.target.value
                        })
                    }
                }, {
                    key: "updateIconURL",
                    value: function (e) {
                        this.setState({
                            iconURL: e.target.value
                        })
                    }
                }, {
                    key: "render",
                    value: function () {
                        var e = this;
                        return l.a.createElement("div", {
                            className: "embed-group embed-footer"
                        }, l.a.createElement("div", {
                            className: "embed-footer-icon"
                        }, l.a.createElement("input", {
                            type: "url",
                            name: "footer:icon_url",
                            placeholder: "Footer Icon URL",
                            value: this.state.iconURL,
                            onChange: function (t) {
                                return e.updateIconURL(t)
                            }
                        })), l.a.createElement("div", {
                            className: "embed-footer-text"
                        }, l.a.createElement("input", {
                            type: "text",
                            name: "footer:text",
                            placeholder: "Footer Text",
                            maxLength: "256",
                            value: this.state.text,
                            onChange: function (t) {
                                return e.updateText(t)
                            }
                        })), l.a.createElement("div", {
                            className: "embed-timestamp"
                        }, l.a.createElement("label", null, l.a.createElement("input", {
                            name: "timestamp",
                            type: "checkbox"
                        }), "Add Timestamp")))
                    }
                }]), n
            }(l.a.Component),
            C = function (e) {
                Object(u.a)(n, e);
                var t = Object(d.a)(n);

                function n() {
                    return Object(c.a)(this, n), t.apply(this, arguments)
                }
                return Object(i.a)(n, [{
                    key: "render",
                    value: function () {
                        return l.a.createElement("div", {
                            className: "cell"
                        }, l.a.createElement("div", {
                            id: "builder-container"
                        }, l.a.createElement("form", {
                            id: "embed-builder"
                        }, l.a.createElement("div", {
                            className: "embed"
                        }, l.a.createElement("div", {
                            className: "embed-content"
                        }, l.a.createElement("div", {
                            className: "embed-content-inner"
                        }, l.a.createElement(m, null), l.a.createElement(s, null), l.a.createElement(b, null), l.a.createElement(h, null), l.a.createElement(p, null), l.a.createElement(f, null), l.a.createElement(g, null), l.a.createElement(E, null), l.a.createElement(k, null), l.a.createElement(j, null), l.a.createElement(y, null)))))))
                    }
                }]), n
            }(l.a.Component),
            O = function (e) {
                Object(u.a)(n, e);
                var t = Object(d.a)(n);

                function n(e) {
                    var a;
                    return Object(c.a)(this, n), (a = t.call(this, e)).state = {
                        result: ""
                    }, a
                }
                return Object(i.a)(n, [{
                    key: "generateJSON",
                    value: function () {
                        var e = document.getElementById("embed-builder"),
                            t = "",
                            n = Boolean(!1),
                            a = e.elements.title.value;
                        a && (n || (n = Boolean(!0)), t += "{title: ".concat(a, "}$v"));
                        var l = e.elements.description.value;
                        l && (n || (n = Boolean(!0)), t += "{description: ".concat(l, "}$v")), e.elements.timestamp.checked && (t += "{timestamp: true}$v");
                        var r = e.elements.url.value;
                        r && (n || (n = Boolean(!0)), t += "{ ".concat(r, "}$v"));
                        var o = e.elements.autodelete.value;
                        o && (t += "{delete: ".concat(o, "}$v"));
                        var c = e.elements["author:url"].value,
                            i = e.elements["author:icon_url"].value,
                            u = e.elements["author:name"].value;
                        if (u) {
                            var d = "author: ".concat(u);
                            i && (d += " && ".concat(i)), c && (i || (d += " && url: None"), d += " && ".concat(c)), n || (n = Boolean(!0)), t += "{".concat(d, "}$v")
                        }
                        var m = document.getElementById("fields").children;
                        if (m.length)
                            for (var s = 0; s < m.length; s++) {
                                var v = e.elements["field-".concat(s, ":name")].value,
                                    b = e.elements["field-".concat(s, ":value")].value,
                                    h = e.elements["field-".concat(s, ":inline")].checked;
                                if (v && b) {
                                    var p = "field: ".concat(v, " && ").concat(b);
                                    p += h ? " && true" : " && false", n || (n = Boolean(!0)), t += "{".concat(p, "}$v")
                                }
                            }
                        var f = e.elements["thumbnail:url"].value;
                        f && (n || (n = Boolean(!0)), t += "{thumbnail: ".concat(f, "}$v"));
                        var g = e.elements["image:url"].value;
                        g && (n || (n = Boolean(!0)), t += "{image: ".concat(g, "}$v"));
                        var E = e.elements["footer:icon_url"].value,
                            y = e.elements["footer:text"].value;
                        if (y) {
                            var j = "footer: ".concat(y);
                            E && (j += " && ".concat(E)), n || (n = Boolean(!0)), t += "{".concat(j, "}$v")
                        }
                        var k = e.elements.color.value;
                        k && n && "#000000" !== (k = "".concat(parseInt(k, 10).toString(16).padStart(6, "0"))) && (t += "{color: #".concat(k, "}$v"));
                        var C = document.getElementById("buttons").children;
                        if (C.length)
                            for (var O = 0; O < C.length; O++) {
                                var L = e.elements["button-".concat(O, ":label")].value,
                                    x = e.elements["button-".concat(O, ":url")].value;
                                if (L && x) {
                                    var N = "button: ".concat(L, " && ").concat(x);
                                    t += "{".concat(N, "}$v")
                                }
                            }
                        var R = e.elements.content.value;
                        R && (t += "{content: ".concat(R, "}$v")), t = t.includes("{embed}") ? t.slice(0, -2) : t, t = n ? "{embed}".concat(t) : t, document.getElementById("json-output").innerHTML = t;
                        var B = document.getElementById("json-output").innerHTML;
                        B = (B = (B = (B = B.replace(/"([\w]*)":/g, '<span class="highlight key">"$1"</span>:')).replace(/(\d*),/g, '<span class="highlight number">$1</span>,')).replace(/: (true|false)/g, ': <span class="highlight boolean">$1</span>')).replace(/: "(.*?)"/g, ': <span class="highlight string">"$1"</span>'), document.getElementById("json-output").innerHTML = B
                    }
                }, {
                    key: "copyJSON",
                    value: function () {
                        var e = document.createElement("textarea");
                        e.id = "temp_element", e.style.height = 0, document.body.appendChild(e), e.value = document.getElementById("json-output").innerText, document.querySelector("#temp_element").select(), document.execCommand("copy"), document.body.removeChild(e)
                    }
                }, {
                    key: "render",
                    value: function () {
                        var e = this;
                        return l.a.createElement("div", {
                            className: "cell"
                        }, l.a.createElement("div", {
                            id: "output-container"
                        }, l.a.createElement("div", {
                            className: "controller"
                        }, l.a.createElement("button", {
                            onClick: function () {
                                return e.generateJSON()
                            }
                        }, l.a.createElement("span", {
                            role: "img",
                            "aria-label": "Gear Emoji"
                        }, "\u2699"), "\u2002Generate Embed Code"), l.a.createElement("button", {
                            onClick: function () {
                                return e.copyJSON()
                            }
                        }, l.a.createElement("span", {
                            role: "img",
                            "aria-label": "Copy Emoji"
                        }, "\ud83d\udd17"), "\u2002Copy Embed Code")), l.a.createElement("div", {
                            className: "output"
                        }, l.a.createElement("pre", null, l.a.createElement("div", {
                            id: "json-output",
                            readOnly: !0
                        }, this.state.result)))))
                    }
                }]), n
            }(l.a.Component),
            L = function (e) {
                Object(u.a)(n, e);
                var t = Object(d.a)(n);

                function n() {
                    return Object(c.a)(this, n), t.apply(this, arguments)
                }
                return Object(i.a)(n, [{
                    key: "render",
                    value: function () {
                        return l.a.createElement("main", null, l.a.createElement(C, null), l.a.createElement(O, null))
                    }
                }]), n
            }(l.a.Component),
            x = (n(193), function (e) {
                Object(u.a)(n, e);
                var t = Object(d.a)(n);

                function n() {
                    return Object(c.a)(this, n), t.apply(this, arguments)
                }
                return Object(i.a)(n, [{
                    key: "render",
                    value: function () {
                        return l.a.createElement("div", {
                            className: "App-container"
                        }, l.a.createElement(L, null))
                    }
                }]), n
            }(l.a.Component)),
            N = Boolean("localhost" === window.location.hostname || "[::1]" === window.location.hostname || window.location.hostname.match(/^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/));

        function R(e) {
            navigator.serviceWorker.register(e).then((function (e) {
                e.onupdatefound = function () {
                    var t = e.installing;
                    t.onstatechange = function () {
                        "installed" === t.state && (navigator.serviceWorker.controller ? console.log("New content is available; please refresh.") : console.log("Content is cached for offline use."))
                    }
                }
            })).catch((function (e) {
                console.error("Error during service worker registration:", e)
            }))
        }
        o.a.render(l.a.createElement(x, null), document.getElementById("__bastion")),
            function () {
                if ("serviceWorker" in navigator) {
                    if (new URL("/embedbuilder", window.location).origin !== window.location.origin) return;
                    window.addEventListener("load", (function () {
                        var e = "".concat("/embedbuilder", "/service-worker.js");
                        N ? (! function (e) {
                            fetch(e).then((function (t) {
                                404 === t.status || -1 === t.headers.get("content-type").indexOf("javascript") ? navigator.serviceWorker.ready.then((function (e) {
                                    e.unregister().then((function () {
                                        window.location.reload()
                                    }))
                                })) : R(e)
                            })).catch((function () {
                                console.log("No internet connection found. App is running in offline mode.")
                            }))
                        }(e), navigator.serviceWorker.ready.then((function () {
                            console.log("This web app is being served cache-first by a service worker. To learn more, visit https://goo.gl/SC7cgQ")
                        }))) : R(e)
                    }))
                }
            }()
    },
    79: function (e, t, n) {
        e.exports = n(194)
    },
    84: function (e, t, n) { }
},
[
    [79, 1, 2]
]
]);
//# sourceMappingURL=main.81ce34e5.chunk.js.map