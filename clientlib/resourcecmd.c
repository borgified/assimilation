/**
 * @file
 * @brief Implements the ResourceCmd factory/parent class
 * @details Detemines which subclass a particular constructor request is for, then
 * executes the relevant subclass constructor.  After that, our only involvement
 * is in the destructor.
 *
 * @author  Alan Robertson <alanr@unix.sh> - Copyright &copy; 2013 - Assimilation Systems Limited
 * @n
 *  This file is part of the Assimilation Project.
 *  The Assimilation software is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  The Assimilation software is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with the Assimilation Project software.  If not, see http://www.gnu.org/licenses/
 */
#include <projectcommon.h>
#include <string.h>
#define	RESOURCECMD_SUBCLASS
#include <resourcecmd.h>

static struct {
	const char *		classname;
	ResourceCmd* (*constructor) (
			guint structsize
,			ConfigContext* request
,			gpointer user_data
,			ResourceCmdCallback callback);
}subclasses[] = {
	{NULL, NULL}
};
void _resourcecmd_finalize(AssimObj*);

/**
 * Our ResourceCmd Factory object - constructs the proper subtype for these instantiation
 * parameters.  We only pay attention to the REQCLASSNAMEFIELD field at the top level
 * of the request ConfigContext object.
 */
ResourceCmd*
resourcecmd_new(ConfigContext* request		///< Request to instantiate
,		gpointer user_data		///< User data for 'callback'
,		ResourceCmdCallback callback)	///< Callback when complete

{
	guint		j;
	const char *	cname;

	if (NULL == request) {
		g_warning("%s.%d: NULL resourcecmd request" , __FUNCTION__, __LINE__);
		return NULL;
	}
	cname = request->getstring(request, REQCLASSNAMEFIELD);

	if (NULL == cname) {
		char *	reqstr = request->baseclass.toString(&request->baseclass);
		g_warning("%s.%d: No class name in request [%s]", __FUNCTION__, __LINE__
		,	reqstr);
		g_free(reqstr); reqstr = NULL;
		return NULL;
	}

	for (j=0; j < DIMOF(subclasses) && subclasses[j].classname; ++j) {
		if (strcmp(cname, subclasses[j].classname) != 0) {
			return subclasses[j].constructor(0, request, user_data, callback);
		}
	}
	g_warning("%s.%d: Invalid resource class [%s]", __FUNCTION__, __LINE__, cname);
	return NULL;
}

/// Finalize function for ResourceCmd objects
void
_resourcecmd_finalize(AssimObj* aself)
{
	ResourceCmd*	self = CASTTOCLASS(ResourceCmd, aself);

	if (self->request) {
		UNREF(self->request);
	}
	self->user_data = NULL;
	self->callback = NULL;
	_assimobj_finalize(aself);
}


/// Constructor (_new function) for ResourceCmd "abstract" class
ResourceCmd*
resourcecmd_constructor(
		guint structsize		///< Structure size (or zero)
,		ConfigContext* request		///< Request to instantiate
,		gpointer user_data		///< User data for 'callback'
,		ResourceCmdCallback callback)	///< Callback when complete
{
	AssimObj*	aself;
	ResourceCmd*	self;

	if (structsize < sizeof(ResourceCmd)) {
		structsize = sizeof(ResourceCmd);
	}
	aself = assimobj_new(structsize);
	self = NEWSUBCLASS(ResourceCmd, aself);

	self->request = request;
	self->user_data = user_data;
	self->callback = callback;

	aself->_finalize = _resourcecmd_finalize;
	return self;
}