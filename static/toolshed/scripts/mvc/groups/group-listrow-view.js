define([],function(){var a=Backbone.View.extend({events:{},initialize:function(a){this.render(a.group)},render:function(a){var b=this.templateRow();return this.setElement(b({group:a})),this.$el.show(),this},templateRow:function(){return _.template(['<tr class="" data-id="<%- group.get("id") %>">','<td><a href="groups#/<%= group.get("id") %>"><%= group.get("name") %></a></td>','<td><%= group.get("total_members") %></td>','<td><%= group.get("total_repos") %></td>',"</tr>"].join(""))}});return{GroupListRowView:a}});
//# sourceMappingURL=../../../maps/mvc/groups/group-listrow-view.js.map