// (C) LiveFlex.co.uk Feb 2011
//
// History:
// 0.1 - Initial release version
// 0.2 - Added saveState, restoreState when jquery.cookie.js is available
//
// TERMS OF USE
// 
// Dual licensed under the MIT and GPL licenses:
// http://www.opensource.org/licenses/mit-license.php
// http://www.gnu.org/licenses/gpl.html
/*
Usage: $('#{0}').liveflex_treeview(
{{
handle:'a.caption'
, dirSelector:'li.parent'
, itemMoved:function(data){{ 
$('#MoveResults').val(data); 
}}
}}
);
*/
(function($) {
	if (!$.liveflex) {
		$.liveflex = new Object();
	};

	$.liveflex.treeview = function(el, options) {
		// To avoid scope issues, use 'base' instead of 'this'
		// to reference this class from internal events and functions.
		var base = this;

		// Access to jQuery and DOM versions of element
		base.$el = $(el);
		base.el = el;

		// Add a reverse reference to the DOM object
		base.$el.data("liveflex.treeview", base);

		base.init = function() {
			base.options = $.extend({}, $.liveflex.treeview.defaultOptions, options);
			//base.$el.delegate('*', 'click', function(e) { handleClick(e) });

			if (base.options.drag) {
				base.$el.find('li ' + base.options.handle).droppable({
					tolerance: "pointer",
					hoverClass: "tree_hover",
					drop: function(event, ui) {
						//console.log(pos.target(), pos.section());
						base.pos.targetX = ui.offset.left;
						base.pos.targetY = $(this).offset().top;
						base.pos.targetH = $(this).height();
						$(this).removeClass('tree_hover');
						var dropped = ui.draggable;
						dropped.css({ top: 0, left: 0 });
						var me = $(this).parent();
						if (me == dropped)
							return;

						ui.draggable.addClass('moved');

						var subbranch = me.children("ul");

						switch (base.pos.target()) {
							case 'on':
								//add as a child
								if (subbranch.size() == 0) {
									//add new ul
									var newb = $('<ul></ul>');
									newb.append(dropped);
									me.append(newb);
								} else {
									subbranch.eq(0).append(dropped);
								}
								if (!me.hasClass('parent')) me.addClass('parent expanded');
								break;
							case 'above':
								//add before
								dropped.insertBefore(me);
								break;
							case 'below':
								//add after
								dropped.insertAfter(me);
								break;
						}
						me.removeClass('on above below');
						//remove parent from items that no longer contain children
						$('ul.tree li.parent ul').filter(function() {
							return $(this).children().length == 0;
						}).closest('li').removeClass('parent').end().remove();
						//callback
						if (base.options.itemMoved != null) {
							base.options.itemMoved(base.getMoved());
						}
					}
					, over: function(e, ui) {
						base.pos.targetX = ui.offset.left;
						base.pos.targetY = $(this).offset().top;
						base.pos.targetH = $(this).height();
					}, out: function(e, ui) {
						$(this).closest('li').removeClass('on above below');
					}
				});

				base.$el.find('li').draggable({
					opacity: 0.3,
					revert: true,
					delay: 300,
					tolerance: 'pointer',
					greedy: 'true',
					drag: function(e, ui) {
						base.pos.sourceX = ui.offset.left;
						base.pos.sourceY = ui.offset.top;

						$('.tree_hover').closest('li').removeClass('on above below').addClass(base.pos.target());
					},
					stop: function(event, ui) {
						base.$el.find('li').removeClass('on above below tree_hover');
					}
				});
			}
			/* hide nested items */
//			base.$el.find('li:has(ul)').addClass('parent collapsed').find('ul').hide();
			/* add last marker for IE */
//			if ($.browser.msie) $('li:last-child').addClass('last');

			//restore state
//			base.restoreState();
		};
		//Open the node based on the selector
		/*base.openNode = function(selector) {
			var item = base.$el.find(selector);
			if (item.length != 0) {
				item.parents('li').add(item).each(function(i) {
					var node = $(this);
					if (node.hasClass('collapsed')) {
						node.find('>ul').slideToggle(0); //need the > selector else all child nodes open
						node.removeClass('collapsed').addClass('expanded');
					}
				});
			}
		};
		*/
		//save the open nodes as a csv
		/*base.saveState = function() {
			var openNodes = '';
			base.$el.find('li.expanded').each(function() {
				openNodes += $(this).attr("data-id") + ',';
			});
			if ($.cookie) $.cookie(base.$el.attr('id') + "treestate", openNodes);
			return openNodes;
		};
		//restore state from csv
		base.restoreState = function(csv) {
			//if we have cookies use those
			if ($.cookie) {
				if ($.cookie(base.$el.attr('id') + "treestate") != undefined) {
					csv = $.cookie(base.$el.attr('id') + "treestate");
				}
			}

			var nodes = csv.split(',');
			for (var id in nodes) {
				base.openNode('li[data-id=' + nodes[id] + ']');
			}
		};
		function handleClick(e) {
			//is the click on me or a child
			var target = $(e.target);
			e.preventDefault();
			e.stopPropagation();
			if (!target.hasClass('noclick')) {//don't react click on child object
				var node = target.closest('li');
				if (node.attr('href') == '#' | node.hasClass('file') | target.is(base.options.callbackSelector)) {
					//its a file node with a href of # so execute the call back
					// if the item that fired the click is not either a folder or a file it cascades as normal
					// so that contained links behave like normal
					base.options.callback(e);
					e.stopPropagation();
				} else if (node.is('.parent') | target.is(base.options.callbackSelector)) { //Is it a directory listitem that fired the click?
					//do collapse/expand
					if (node.hasClass('collapsed')) {
						node.find('>ul').slideToggle('fast'); //need the > selector else all child nodes open
						node.removeClass('collapsed').addClass('expanded');
					}
					else if (node.hasClass('expanded')) {
						node.find('>ul').slideToggle('fast');
						node.removeClass('expanded').addClass('collapsed');
					}
					if (base.options.dirClick != undefined) base.options.dirClick($(node));
					//its one of our directory nodes so stop propagation
					e.stopPropagation();

				} else {
					//node
					if (base.options.nodeClick != undefined) base.options.nodeClick(node);
				}
			}
			//save the state of the nodes
			base.saveState();
			return false;
		}
		*/
		base.getMoved = function() {
			var result = '';
			base.$el.find('.moved').each(function(i) {
				var li = $(this);
				var parentli = li.parent().closest('li');
				var position = li.parent().find('> li').index(li) + 1;
				result += li.attr('data-id') + '-' + parentli.attr('data-id') + '.' + position + ',';
			});
			return result;
		};
		//parse the tree into a json structured array
		/*base.parseTree = function(ul) {
			if (ul == undefined) ul = base.$el;
			var tags = [];
			ul.children("li").each(function() {
				var subtree = $(this).children("ul");
				if (subtree.size() > 0)
					tags.push([$(this).attr("data-id"), base.parseTree(subtree)]);
				else
					tags.push($(this).attr("data-id"));
			});
			return tags;
		};*/
		base.parseTree = function(ul) {
			if (ul == undefined) ul = base.$el;
			var tags = [];
			ul.find("li").each(function() {
				var parent = $(this).parent('ul').closest('li');
				tags.push({id:$(this).data("id"), order:$(this).data("order"), parent:parent.data("id")||0});
			});
			return tags;
		};

		base.pos = {
			sourceX: 0
			, sourceY: 0
			, targetX: 0
			, targetY: 0
			, targetH: 0
			, section: function() {
				return (this.targetY - this.sourceY);
			},
			target: function() {
				var sec = base.pos.section();
				var offset = base.options.dropOffset;
				if (sec < offset && sec > (0 - offset)) return 'on';
				if (sec >= (0 - offset)) return 'above';
				if (sec <= offset) return 'below';
			}
		}

		// Run initializer
		base.init();
		return base;
	};

	$.liveflex.treeview.defaultOptions = {
		dropOffset: 5, 		//Sensitivity to drop location in pixels
		handle: 'span', 		//the item that the drag operation is tied to
		callbackSelector: '', //selector that fires the callback passed in below
		callback: null, 		//callback that is fired when callbackSelector is clicked
		itemMoved: null, 	//fired when an item is moved
		dirClick: null, 		//fired when a directory is clicked
		nodeClick: null, 	//fired when a node is clicked
		drag: true				//enable drag and drop behavior, requires jquery ui
	};

	$.fn.liveflex_treeview = function(options) {
		return this.each(function() {
			(new $.liveflex.treeview(this, options));
		});
	};

	// This function breaks the chain, but returns
	// the liveflex.treeview if it has been attached to the object.
	$.fn.getliveflex_treeview = function() {
		this.data("liveflex.treeview");
	};

})(jQuery);