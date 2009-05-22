<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://genshi.edgewall.org/" xmlns:xi="http://www.w3.org/2001/XInclude">
    <xi:include py:if="'master' in cmf and not isinstance(cmf.master, list)" href="${cmf.master}" />
    <xi:include py:if="'master' in cmf and isinstance(cmf.master, list)" py:for="master in cmf.master" href="${master}" />
    
    <head>
        <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
        
        <title py:content="asset.title">Untitled</title>
        
        <meta py:if="asset.description" name="description" py:attrs="{'content': asset.description}" />
        <meta py:if="asset.tags" name="keywords" py:attrs="{'content': ', '.join([tag for tag in asset.tags if ':' not in tag])}" />
    </head>
    
    <body>
        <div class="yui-b">
            <h2 py:content="'Modifying %s Properties' % asset.__class__.__name__">Modifying Asset Properties</h2>
            
            <div class="content">
                <form id="form" method="post" class="serial">
                    <h3>General</h3>
                    
                    <div class="yui-g" style="margin-bottom: 15px;">
                        <div class="yui-u first">
                            <div class="field">
                                <label for="guid">Asset <acronym title="Globally Unique Identifier">GUID</acronym></label>
                                <div class="help">This is the read-only unique identifier for this asset.</div>
                                <div><input type="text" name="guid" py:attrs="{'value': asset.guid}" id="guid" disabled="True" class="disabled" /></div>
                            </div>
                        </div>
                        <div class="yui-u">
                            <div class="field">
                                <label for="name">Asset Name</label>
                                <div class="help">The container-unique name for this asset.</div>
                                <div style="padding-right: 7px;"><input type="text" name="name" id="name" py:attrs="{'value': asset.name}" /></div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="field">
                        <label for="tags">Tags</label>
                        <div class="help">Tags (keywords) associated with this asset.</div>
                        <div><input type="text" name="tags" id="tags" py:attrs="{'value': ' '.join((i if ' ' not in i else '\x22'+i+'\x22') for i in asset.tags)}" /></div>
                    </div>
                    
                    <div class="field">
                        <label for="owner">Owner</label>
                        <div class="help">The account or entity with ownership rights over this asset.</div>
                        <div><input type="text" name="owner" py:attrs="{'value': asset.owner.name if asset.owner else 'None'}" id="owner" disabled="True" class="disabled" /></div>
                    </div>
                    
                    <h3>Simple Workflow</h3>
                            
                    <div class="yui-g" style="margin-bottom: 15px;">
                        <div class="yui-u first">
                            <div class="field">
                                <label for="published">Publication Date</label>
                                <div class="help">This asset will become accessible after this date and time, if given. Dates must be entered in <i>YYYY/MM/DD HH:MM</i> 24-hour format.</div>
                                <div><input type="text" name="published" id="published" py:attrs="{'value': asset.published.strftime('%Y/%m/%d %H:%M') if asset.published else ''}" /></div>
                            </div>
                        </div>
                        <div class="yui-u">
                            <div class="field">
                                <label for="retracted">Retraction Date</label>
                                <div class="help">This asset will cease being available after this date and time, if given. Dates must be entered in <i>YYYY/MM/DD HH:MM</i> 24-hour format.</div>
                                <div><input type="text" name="retracted" id="retracted" py:attrs="{'value': asset.retracted.strftime('%Y/%m/%d %H:%M') if asset.retracted else ''}" /></div>
                            </div>
                        </div>
                    </div>
                            
                    <h3>Default Display</h3>
                    
                    <div class="field">
                        <label for="default">Default View or Asset to Display</label>
                        <div class="help">This is the default view users will see when first navigating to this asset.  Selecting another asset as the default view simulates the behavior of an "index.html" file.</div>
                        <div>
                            <select name="default" id="default">
                                <option value="view:default">Asset's Default View</option>
                                <optgroup label="Available Views">
                                    <option py:for="name, view in controller.views" value="view:${name}" py:content="view.title" py:attrs="{'selected': 'True'} if (asset.default == 'view:' + name) else {}" />
                                </optgroup>
                                <optgroup label="Child Assets" py:if="asset.children">
                                    <option py:for="child in asset.children" value="${child.name}" py:content="repr(child)" py:attrs="{'selected': 'True'} if asset.default == child.name else {}" />
                                </optgroup>
                            </select>
                        </div>
                    </div>
                        
                    <div class="footer">
                        <ul class="actions buttons right">
                            <li><button type="submit" class="button positive icon submit">Save Changes</button></li
                            ><li><a class="button negative icon close" py:attrs="{'href': tg.url(asset.path) + '/'}" onclick="return confirm('Are you sure?  Any unsaved changes will be lost.');">Cancel</a></li>
                        </ul>
                        <div style="clear: both;"><!-- IE --></div>
                    </div>
                </form>
            </div>
        </div>
    </body>
</html>