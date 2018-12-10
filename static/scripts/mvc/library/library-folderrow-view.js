define(["layout/masthead","utils/utils","libs/toastr","mvc/library/library-model","mvc/library/library-dataset-view"],function(a,b,c,d,e){var f=Backbone.View.extend({lastSelectedHistory:"",events:{"click .undelete_dataset_btn":"undeleteDataset","click .undelete_folder_btn":"undeleteFolder"},options:{type:null},initialize:function(a){this.model=a,this.render(a)},render:function(a){var b=null;return"folder"===a.get("type")||"LibraryFolder"===a.get("model_class")?(this.options.type="folder",b=a.get("deleted")?this.templateRowDeletedFolder():this.templateRowFolder()):"file"===a.get("type")||"LibraryDatasetDatasetAssociation"===a.get("model_class")?(this.options.type="file",b=a.get("deleted")?this.templateRowDeletedFile():this.templateRowFile()):(console.error("Unknown library item type found."),console.error(a.get("type")||a.get("model_class"))),this.setElement(b({content_item:a})),this.$el.show(),this},showDatasetDetails:function(){Galaxy.libraries.datasetView=new e.LibraryDatasetView({id:this.id})},undeleteDataset:function(a){$(".tooltip").hide();var b=this,e=$(a.target).closest("tr")[0].id,f=Galaxy.libraries.folderListView.collection.get(e);f.url=f.urlRoot+f.id+"?undelete=true",f.destroy({success:function(a,f){Galaxy.libraries.folderListView.collection.remove(e);var g=new d.Item(f);Galaxy.libraries.folderListView.collection.add(g),Galaxy.libraries.folderListView.collection.sortByNameAsc(),c.success("Dataset undeleted. Click this to see it.","",{onclick:function(){var a=b.model.get("folder_id");window.location="#folders/"+a+"/datasets/"+b.id}})},error:function(a,b){c.error("undefined"!=typeof b.responseJSON?"Dataset was not undeleted. "+b.responseJSON.err_msg:"An error occured! Dataset was not undeleted. Please try again.")}})},undeleteFolder:function(a){$(".tooltip").hide();var b=$(a.target).closest("tr")[0].id,e=Galaxy.libraries.folderListView.collection.get(b);e.url=e.urlRoot+e.id+"?undelete=true",e.destroy({success:function(a,e){Galaxy.libraries.folderListView.collection.remove(b);var f=new d.FolderAsModel(e);Galaxy.libraries.folderListView.collection.add(f),Galaxy.libraries.folderListView.collection.sortByNameAsc(),c.success("Folder undeleted.")},error:function(a,b){c.error("undefined"!=typeof b.responseJSON?"Folder was not undeleted. "+b.responseJSON.err_msg:"An error occured! Folder was not undeleted. Please try again.")}})},templateRowFolder:function(){return tmpl_array=[],tmpl_array.push('<tr class="folder_row light library-row" id="<%- content_item.id %>">'),tmpl_array.push("  <td>"),tmpl_array.push('    <span title="Folder" class="fa fa-folder-o"></span>'),tmpl_array.push("  </td>"),tmpl_array.push('  <td style="text-align: center; "><input style="margin: 0;" type="checkbox"></td>'),tmpl_array.push("  <td>"),tmpl_array.push('    <a href="#folders/<%- content_item.id %>"><%- content_item.get("name") %></a>'),tmpl_array.push("  </td>"),tmpl_array.push("  <td>folder</td>"),tmpl_array.push("  <td></td>"),tmpl_array.push('  <td><%= _.escape(content_item.get("update_time")) %></td>'),tmpl_array.push("  <td>"),tmpl_array.push('    <% if (content_item.get("can_manage")) { %><a href="#/folders/<%- content_item.id %>/permissions"><button data-toggle="tooltip" data-placement="top" class="primary-button btn-xs permissions-folder-btn show_on_hover" title="Manage permissions" style="display:none;"><span class="fa fa-group"></span></button></a><% } %>'),tmpl_array.push("  </td>"),tmpl_array.push("</tr>"),_.template(tmpl_array.join(""))},templateRowFile:function(){return tmpl_array=[],tmpl_array.push('<tr class="dataset_row light library-row" id="<%- content_item.id %>">'),tmpl_array.push("  <td>"),tmpl_array.push('    <span title="Dataset" class="fa fa-file-o"></span>'),tmpl_array.push("  </td>"),tmpl_array.push('  <td style="text-align: center; "><input style="margin: 0;" type="checkbox"></td>'),tmpl_array.push('  <td><a href="#folders/<%- content_item.get("folder_id") %>/datasets/<%- content_item.id %>" class="library-dataset"><%- content_item.get("name") %><a></td>'),tmpl_array.push('  <td><%= _.escape(content_item.get("file_ext")) %></td>'),tmpl_array.push('  <td><%= _.escape(content_item.get("file_size")) %></td>'),tmpl_array.push('  <td><%= _.escape(content_item.get("update_time")) %></td>'),tmpl_array.push("  <td>"),tmpl_array.push('    <% if (content_item.get("is_unrestricted")) { %><span data-toggle="tooltip" data-placement="top" title="Unrestricted dataset" style="color:grey;" class="fa fa-globe fa-lg"></span><% } %>'),tmpl_array.push('    <% if (content_item.get("is_private")) { %><span data-toggle="tooltip" data-placement="top" title="Private dataset" style="color:grey;" class="fa fa-key fa-lg"></span><% } %>'),tmpl_array.push('    <% if ((content_item.get("is_unrestricted") === false) && (content_item.get("is_private") === false)) { %><span data-toggle="tooltip" data-placement="top" title="Restricted dataset" style="color:grey;" class="fa fa-shield fa-lg"></span><% } %>'),tmpl_array.push('    <% if (content_item.get("can_manage")) { %><a href="#folders/<%- content_item.get("folder_id") %>/datasets/<%- content_item.id %>/permissions"><button data-toggle="tooltip" data-placement="top" class="primary-button btn-xs permissions-dataset-btn show_on_hover" title="Manage permissions" style="display:none;"><span class="fa fa-group"></span></button></a><% } %>'),tmpl_array.push("  </td>"),tmpl_array.push("</tr>"),_.template(tmpl_array.join(""))},templateRowDeletedFile:function(){return tmpl_array=[],tmpl_array.push('<tr class="active deleted_dataset library-row" id="<%- content_item.id %>">'),tmpl_array.push("  <td>"),tmpl_array.push('    <span title="Dataset" class="fa fa-file-o"></span>'),tmpl_array.push("  </td>"),tmpl_array.push("  <td></td>"),tmpl_array.push('  <td style="color:grey;"><%- content_item.get("name") %></td>'),tmpl_array.push('  <td><%= _.escape(content_item.get("file_ext")) %></td>'),tmpl_array.push('  <td><%= _.escape(content_item.get("file_size")) %></td>'),tmpl_array.push('  <td><%= _.escape(content_item.get("update_time")) %></td>'),tmpl_array.push('  <td><span data-toggle="tooltip" data-placement="top" title="Marked deleted" style="color:grey;" class="fa fa-ban fa-lg"> </span><button data-toggle="tooltip" data-placement="top" title="Undelete <%- content_item.get("name") %>" class="primary-button btn-xs undelete_dataset_btn show_on_hover" type="button" style="display:none; margin-left:1em;"><span class="fa fa-unlock"> Undelete</span></button></td>'),tmpl_array.push("</tr>"),_.template(tmpl_array.join(""))},templateRowDeletedFolder:function(){return tmpl_array=[],tmpl_array.push('<tr class="active deleted_folder light library-row" id="<%- content_item.id %>">'),tmpl_array.push("  <td>"),tmpl_array.push('    <span title="Folder" class="fa fa-folder-o"></span>'),tmpl_array.push("  </td>"),tmpl_array.push("  <td></td>"),tmpl_array.push('  <td style="color:grey;">'),tmpl_array.push('    <%- content_item.get("name") %>'),tmpl_array.push("  </td>"),tmpl_array.push("  <td>folder</td>"),tmpl_array.push("  <td></td>"),tmpl_array.push('  <td><%= _.escape(content_item.get("update_time")) %></td>'),tmpl_array.push('  <td><span data-toggle="tooltip" data-placement="top" title="Marked deleted" style="color:grey;" class="fa fa-ban fa-lg"> </span><button data-toggle="tooltip" data-placement="top" title="Undelete <%- content_item.get("name") %>" class="primary-button btn-xs undelete_folder_btn show_on_hover" type="button" style="display:none; margin-left:1em;"><span class="fa fa-unlock"> Undelete</span></button></td>'),tmpl_array.push("</tr>"),_.template(tmpl_array.join(""))}});return{FolderRowView:f}});
//# sourceMappingURL=../../../maps/mvc/library/library-folderrow-view.js.map