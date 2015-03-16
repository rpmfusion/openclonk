%global develdocdir %{_docdir}/%{name}-devel/html

Name:           openclonk
Version:        6.0
Release:        1%{?dist}
Summary:        Fast-paced 2d genre mix
License:        ISC and CC-BY-SA
Url:            http://www.openclonk.org/
Source0:        http://www.openclonk.org/builds/release/%{version}/%{name}-%{version}-src.tar.bz2
Source1:        %{name}.appdata.xml
Source2:        %{name}-html-de.desktop
Source3:        %{name}-html-en.desktop
Source4:        %{name}-docs.png
Patch0:         %{name}-%{version}-target.patch
BuildRequires:  boost-devel
BuildRequires:  cmake
BuildRequires:  gtest-devel
BuildRequires:  libjpeg-devel
BuildRequires:  tinyxml-devel
BuildRequires:  pkgconfig(SDL_mixer)
BuildRequires:  pkgconfig(dri)
BuildRequires:  pkgconfig(freealut)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:  pkgconfig(gl)
BuildRequires:  pkgconfig(glew)
BuildRequires:  pkgconfig(gtk+-2.0)
BuildRequires:  pkgconfig(gtksourceview-2.0)
BuildRequires:  pkgconfig(libpng12)
BuildRequires:  pkgconfig(libupnp)
BuildRequires:  pkgconfig(ogg)
BuildRequires:  pkgconfig(sdl)
BuildRequires:  pkgconfig(vorbis)
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xpm)
BuildRequires:  pkgconfig(xrandr)
BuildRequires:  pkgconfig(xxf86vm)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  pkgconfig(xml2po)
BuildRequires:  ImageMagick
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib
BuildRequires:  libxslt
BuildRequires:  gettext
BuildRequires:  libxml2-devel
Requires:       hicolor-icon-theme
Provides:       bundled(timsort)
Requires:       %{name}-data = %{version}-%{release}

%description
Clonk is a multiplayer-action-tactics-skill game. It is often referred to as
a mixture of The Settlers and Worms. In a simple 2D ant-farm style landscape,
the player controls his crew of Clonks, small but robust humanoid beings.
The game encourages free play but the normal goal is to either exploit
valuable resources from the earth by building a mine or fight each other on
an arena-like map.

%package data
Summary:        Graphic Objects for %{name}
BuildArch:      noarch
Requires:       %{name} = %{version}-%{release}

%description data
Arch-independent data files for OpenClonk.
This package contains images, themes and JavaScript.

%package devel-docs
Summary:        Documentation for developing programs that will use %{name}
Group:          Documentation
BuildArch:      noarch
Requires:       xdg-utils

%description devel-docs
This package contains documentation needed for developing with %{name}.

%prep
%setup -q -n %{name}-release-%{version}-src
%patch0 -p1 -b .target

# remove bundled tinyxml
rm -rf thirdparty/tinyxml
# remove bundled getopt
rm -rf thirdparty/getopt
# remove bundled natupnp
rm -rf thirdparty/natupnp
rm -rf planet/Tests.c4f
# change permission in src and docs folder
find src -type f | xargs chmod -v 644
find docs -type f | xargs chmod -v 644
find docs -type d | xargs chmod -v 755

# change permission due rpmlint W: spurious-executable-perm
chmod a-x README Credits.txt thirdparty/timsort/sort.h

# change permission due rpmlint E: script-without-shebang
chmod -x COPYING TRADEMARK
chmod -x licenses/*

%build
%cmake -DUSE_STATIC_BOOST=OFF \
       -DWITH_SYSTEM_TINYXML=ON \
       -DBUILD_SHARED_LIBS=OFF

make %{?_smp_mflags}

# build the German and English HTML-documentation from the English \
# XML-source files and the translation file
pushd docs
mkdir -p sdk-de/{definition,folder,material,particle,scenario,script/fn}
make %{?_smp_mflags} chm/de/Entwickler.chm
make %{?_smp_mflags} chm/en/Developer.chm
popd

%install
make DESTDIR=%{buildroot} install
mv %{buildroot}%{_prefix}/games/%{name} %{buildroot}%{_bindir}/%{name}

# install appdata.xml file
mkdir -p %{buildroot}%{_datadir}/appdata
install -Dm 0644 %{SOURCE1} %{buildroot}%{_datadir}/appdata/%{name}.appdata.xml

# install html docs to %%{_docdir}/%%{name}-devel/html
mkdir -p %{buildroot}%{develdocdir}/{de,en}
cp -pr docs/chm/de %{buildroot}/%{develdocdir}/
cp -pr docs/chm/en %{buildroot}/%{develdocdir}/

# W: wrong-file-end-of-line-encoding
sed -i 's/\r$//' %{buildroot}/%{develdocdir}/de/Output.hhp
sed -i 's/\r$//' %{buildroot}/%{develdocdir}/en/Output.hhp

# W: file-not-utf8
iconv -f iso8859-1 -t utf-8 %{buildroot}/%{develdocdir}/de/Output.hhk > \
Output.hhk.conv && mv -f Output.hhk.conv %{buildroot}/%{develdocdir}/de/Output.hhk

# HTML desktop files
desktop-file-install --dir %{buildroot}%{_datadir}/applications %{SOURCE2}
desktop-file-install --dir %{buildroot}%{_datadir}/applications %{SOURCE3}
mkdir -p %{buildroot}%{_datadir}/pixmaps
install -D -m 0644 %{SOURCE4} $RPM_BUILD_ROOT%{_datadir}/pixmaps/%{name}-docs.png

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/*.desktop
appstream-util validate-relax --nonet %{buildroot}%{_datadir}/appdata/*.appdata.xml

%post
/usr/bin/update-desktop-database &> /dev/null || :
/bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
/usr/bin/update-desktop-database &> /dev/null || :
if [ $1 -eq 0 ] ; then
    /bin/touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    /usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
/usr/bin/gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%files
%doc README Credits.txt
%license licenses/*.txt
%license COPYING TRADEMARK
%{_bindir}/*
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_datadir}/applications/%{name}.desktop
%{_datadir}/appdata/%{name}.appdata.xml

%files data
%license licenses/*.txt
%license COPYING TRADEMARK
%{_datadir}/%{name}

%files devel-docs
%dir %{_docdir}/%{name}-devel
%doc %{develdocdir}
%{_datadir}/applications/%{name}-html-*.desktop
%{_datadir}/pixmaps/%{name}-docs.png

%changelog
* Mon Mar 16 2015 Martin Gansser <martinkg@fedoraproject.org> - 6.0-1
- Update to 6.0
- correct %%license tag
- cleanup spec file

* Tue Feb 24 2015 Martin Gansser <martinkg@fedoraproject.org> - 5.5.1-6
- dropped CFLAGS and CXXFLAGS flags because already sets by %%cmake macro
- dropped CMAKE_INSTALL_PREFIX because already sets by %%cmake macro
- removed bundled natupnp
- added virtual provides for tracking purposes

* Sun Feb 22 2015 Martin Gansser <martinkg@fedoraproject.org> - 5.5.1-5
- changed permission of files in src folder 
- dropped GPLv2+ and ISC license
- correct spelling errors
- removed bundled getopt
- removed BSD license
- added ISC license
- replaced license CC-BY-SA by CC-BY-NC
- dropped GenericName entry from desktop file due display issue

* Sat Feb 21 2015 Martin Gansser <martinkg@fedoraproject.org> - 5.5.1-4
- added BR desktop-file-utils
- replaced tabs by space

* Fri Feb 20 2015 Martin Gansser <martinkg@fedoraproject.org> - 5.5.1-3
- corrected requirements to pkgconfig(xml2po)
- deleted Requieres from sub package
- added Requires to main package
- added html desktop files
- replaced tabs by space
- added RR xdg-utils to docs package
- added %%{?_smp_mflags} flag to html make
- added png file to devel-docs package

* Thu Feb 19 2015 Martin Gansser <martinkg@fedoraproject.org> - 5.5.1-2
- deleted group tag
- added doc tag
- added license tag
- added appdata.xml file
- changed file permission
- used macro %%cmake
- corrected RR dependencies
- added %%licenses to main package
- added %%licenses to sub package
- added BR tinyxml-devel
- added BR pkgconfig(xml2po)
- added BR libxslt
- added BR libxml2-devel
- installed html docs

* Tue Jan 27 2015 Martin Gansser <martinkg@fedoraproject.org> - 5.5.1-1
- initial build for Fedora 21

